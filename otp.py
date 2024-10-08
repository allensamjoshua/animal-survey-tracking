import random
import smtplib
from email.message import EmailMessage

# Step 1: Generate OTP
def generate_otp():
    otp = random.randint(100000, 999999)
    return otp

# Step 2: Send OTP to Email
def send_otp_via_email(otp, receiver_email):
    sender_email = "allensamjoshua2003@gmail.com"  # Enter your emailotp.py
    sender_password = "qbhu pwzo fnxg ydyh"      # Enter your email app password

    msg = EmailMessage()
    msg.set_content(f"Your OTP is {otp}")
    msg['Subject'] = "Your OTP Code"
    msg['From'] = sender_email
    msg['To'] = receiver_email

    # Use Gmail SMTP server (you can adjust for other providers)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender_email, sender_password)
        smtp.send_message(msg)

# Step 3: Validate OTP
def validate_otp(sent_otp):
    user_otp = int(input("Enter the OTP sent to your email: "))
    if user_otp == sent_otp:
        print("OTP is valid!")
    else:
        print("Invalid OTP, please try again.")

# Main Function
if __name__ == "__main__":
    email = input("Enter your email address: ")
    otp = generate_otp()
    send_otp_via_email(otp, email)
    print("OTP sent successfully!")

    # Now validate the OTP entered by the user
    validate_otp(otp)
