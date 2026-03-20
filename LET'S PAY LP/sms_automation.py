import requests
from flask import Flask, request, jsonify
import time

# ==============================================================================
# BCA PROJECT: AUTOMATED SMS PAYMENT CONFIRMATION SYSTEM
# ==============================================================================
# This script acts as a localized "Backend Server" for your project.
# It uses the concept of "Webhooks" to detect when a payment occurs.
#
# WHAT IS A WEBHOOK?
# Think of a Webhook as a "notification bell". Instead of your code constantly 
# asking "Did the payment finish?" (Polling), the Payment Gateway (or your Frontend)
# automatically pushes data to this script via a URL (e.g., /payment-success) 
# the moment the transaction is complete.
# ==============================================================================

app = Flask(__name__)

# --- CONFIGURATION (Enter your API Details Here) ---
# We are using Fast2SMS (popular in India) for this demo. 
# You can switch to Twilio/Vonage by changing the URL parameters.
SMS_API_KEY = "YOUR_API_KEY_HERE" 
SMS_PROVIDER_URL = "https://www.fast2sms.com/dev/bulkV2"

def send_confirmation_sms(mobile_number, amount, txt_id):
    """
    Sends an SMS using the requests library.
    """
    try:
        print(f"\n[Action] Initiating SMS to {mobile_number}...")
        
        # Message Content
        message_text = f"Hello! Your payment of INR {amount} has been received successfully. TxnID: {txt_id}. Thank you! - SwiftPay"
        
        # Payload for Fast2SMS API
        payload = {
            "authorization": SMS_API_KEY,
            "message": message_text,
            "language": "english",
            "route": "q",
            "numbers": mobile_number
        }
        
        # HEADERS
        headers = {
            'cache-control': "no-cache"
        }

        # --- THE AUTOMATION STEP ---
        # Sending the request to the SMS Gateway
        if SMS_API_KEY == "YOUR_API_KEY_HERE":
             print("[Simulation] No API Key found. Simulating sending...")
             time.sleep(1) # Simulate network delay
             print(f"[Success] Virtual SMS sent to {mobile_number}: '{message_text}'")
             return True

        response = requests.get(SMS_PROVIDER_URL, headers=headers, params=payload)
        
        # Logging the output
        print(f"[API Response] {response.text}")
        return True

    except Exception as e:
        print(f"[Error] Failed to send SMS: {e}")
        return False

# --- WEBHOOK LISTENER ---
# This function 'listens' for the signal from your Payment App
@app.route('/payment-webhook', methods=['POST'])
def payment_success_webhook():
    """
    This is the Webhook Receiver. It waits for the Payment Gateway to hit this URL.
    """
    print("\n[Webhook] Incoming Payment Signal Detected!")
    
    # 1. Parse the incoming data (Input Data)
    data = request.json
    recipient_mobile = data.get('recipient_mobile_number')
    transaction_amount = data.get('transaction_amount')
    transaction_id = data.get('transaction_id', 'TXN0000')

    if not recipient_mobile or not transaction_amount:
        return jsonify({"status": "error", "message": "Missing Data"}), 400

    print(f"[Data] Payment Confirmed: ₹{transaction_amount} from {recipient_mobile}")

    # 2. Trigger the Automation (Action)
    sms_sent = send_confirmation_sms(recipient_mobile, transaction_amount, transaction_id)

    if sms_sent:
        return jsonify({"status": "success", "message": "SMS Triggered Successfully"}), 200
    else:
        return jsonify({"status": "failed", "message": "SMS Failed"}), 500

if __name__ == "__main__":
    print(">>> BCA Project Payment Listener is RUNNING...")
    print(">>> Waiting for Payment Webhooks on http://localhost:5000/payment-webhook")
    # Run the server
    app.run(port=5000, debug=True)
