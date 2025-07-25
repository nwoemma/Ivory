from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import CustomUser
from chat.models import ChatRoom, Message, PrivateMessage
from chat.forms import MessageForm, PrivateMessageForm
from .models import Appointment
from .forms import AppointmentForm
from doctor.models import DoctorProfile, DoctorAppointment
from contact.forms import ContactForm
from contact.models import Contact
from django.contrib.auth import get_user_model


User = get_user_model()

@login_required
def patient_chat_room_list(request):
    chat_rooms = ChatRoom.objects.filter(users=request.user)
    return render(request, "patients/chat_room_list.html", {"chat_rooms": chat_rooms})


@login_required
def patient_chat_room_detail(request, pk):
    chat_room = get_object_or_404(ChatRoom, pk=pk)
    messages = Message.objects.filter(chat_room=chat_room).order_by("timestamp")

    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]
            Message.objects.create(
                user=request.user, chat_room=chat_room, content=content
            )
            return redirect("patients:patient_chat_room_detail", pk=pk)
    else:
        form = MessageForm()

    return render(
        request,
        "patients/chat_room_detail.html",
        {"chat_room": chat_room, "messages": messages, "form": form},
    )


@login_required
def patient_private_message_list(request):
    users = CustomUser.objects.exclude(username=request.user.username)
    return render(request, "patients/private_message_list.html", {"users": users})


@login_required
def patient_private_message_detail(request, username):
    recipient = get_object_or_404(CustomUser, username=username)
    messages = PrivateMessage.objects.filter(
        sender=request.user, recipient=recipient
    ) | PrivateMessage.objects.filter(
        sender=recipient, recipient=request.user
    ).order_by(
        "timestamp"
    )

    if request.method == "POST":
        form = PrivateMessageForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]
            PrivateMessage.objects.create(
                sender=request.user, recipient=recipient, content=content
            )
            return redirect(
                "patients:patient_private_message_detail", username=username
            )
    else:
        form = PrivateMessageForm()

    return render(
        request,
        "patients/private_message_detail.html",
        {"recipient": recipient, "messages": messages, "form": form},
    )


@login_required
def patient_appointments(request):
    user = request.user
    appointments = Appointment.objects.filter(patient=user)

    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = user
            appointment.status = "scheduled"  # Default status for patients
            appointment.nurse = None  # Set nurse to None initially
            appointment.save()
            print("Appointment saved with status:", appointment.status)
            return redirect("patients:patient_appointments")
        else:
            print("Form errors:", form.errors)
    else:
        form = AppointmentForm()

    return render(
        request,
        "patients/patient_appointments.html",
        {"appointments": appointments, "form": form},
    )


@login_required
def update_appointment_status(request, pk, status):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.user.role == "patients" and appointment.doctor == request.user:
        appointment.status = status
        appointment.save()
    return redirect("patients:patient_appointments_view")


@login_required
def patient_contact(request):
    if request.user.role != "patient":
        return redirect("pages:authenticated_home")

    if request.method == "POST":
        form = ContactForm(request.POST, request.FILES, request=request)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.user = request.user
            
            # Determine recipient based on recipient_role
            recipient_role = form.cleaned_data.get("recipient_role")
            if recipient_role == "doctor":
                # Example logic to find a doctor user
                contact.recipient = User.objects.filter(role="doctor").first()  # Adjust according to your logic
            elif recipient_role == "patient":
                contact.recipient = request.user  # Or another user if necessary

            contact.save()
            return redirect("patients:patient_messages")
    else:
        form = ContactForm(request=request)

    return render(request, "patients/patient_contact.html", {"form": form})



@login_required
def patient_messages(request):
    # Check if the user's role is exactly "patient"
    if request.user.role.lower() != "patient":
        return redirect("pages:authenticated_home")

    messages = Contact.objects.filter(recipient_role="doctor", user=request.user)
    return render(request, "patients/patients_messages.html", {"messages": messages})
