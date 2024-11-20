import razorpay  # Razorpay client library
import webview  # Use pywebview instead of webview
from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import BoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog


# Razorpay API credentials (Test Mode)
RAZORPAY_KEY_ID = 'rzp_test_hf2afT5lk394ug'
RAZORPAY_KEY_SECRET = 'bSTTNZLyxYZXdNzb2aRUHLvT'

# Initialize Razorpay client
client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

def create_razorpay_order(amount_in_paise):
    try:
        order_data = client.order.create({
            "amount": amount_in_paise,
            "currency": "INR",
            "receipt": "receipt#1",
            "payment_capture": 1
        })
        if order_data.get("id"):
            print(f"Razorpay Order Created Successfully: {order_data['id']}")
            return order_data
        else:
            print("Error: Order data does not contain an ID")
            return None
    except Exception as e:
        print(f"Error creating Razorpay order: {str(e)}")
        return None

KV = '''
BoxLayout:
    orientation: "vertical"
    spacing: 10
    padding: 10

    MDLabel:
        text: "Enter the amount for Razorpay Payment"
        theme_text_color: "Secondary"

    MDTextField:
        id: amount_input
        hint_text: "Amount in INR"
        mode: "rectangle"
        input_filter: "int"
        max_text_length: 10
        helper_text: "Enter amount in INR"
        helper_text_mode: "on_focus"

    MDRaisedButton:
        text: "Pay Now"
        on_release: app.pay_now()
'''

class Kishore(MDApp):
    def build(self):
        # Set the window size for the entire Kivy application window
        # Set the height and width of the window
        return Builder.load_string(KV)

    def pay_now(self):
        """
        Function to handle the payment process when 'Pay Now' is clicked.
        It creates an order on Razorpay and opens Razorpay checkout in a pywebview.
        """
        # Get the entered amount from the MDTextInput field
        amount_input = self.root.ids.amount_input.text

        if not amount_input:
            # Show an alert dialog if no amount is entered
            dialog = MDDialog(
                title="Error",
                text="Please enter a valid amount",
                size_hint=(0.7, 1)
            )
            dialog.open()
            return

        try:
            # Convert the amount to paise (1 INR = 100 paise)
            amount_in_paise = int(amount_input) * 100
        except ValueError:
            # Show an error dialog if the amount is invalid
            dialog = MDDialog(
                title="Invalid Amount",
                text="Please enter a valid number",
                size_hint=(0.7, 1)
            )
            dialog.open()
            return

        # Create order and get order details from Razorpay API
        order_data = create_razorpay_order(amount_in_paise)
        if order_data:
            order_id = order_data['id']
            amount = order_data['amount']
            currency = order_data['currency']

            # Create Razorpay checkout options in HTML/JavaScript
            checkout_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
            </head>
            <body>
                <script>
                    var options = {{
                        key: '{RAZORPAY_KEY_ID}',  // Razorpay API Key
                        amount: {amount},  // Amount in paise (integer)
                        currency: '{currency}',
                        name: 'Your Company',
                        description: 'Test Payment',
                        order_id: '{order_id}',  // Order ID from Razorpay API
                        handler: function(response) {{
                            alert('Payment successful: ' + response.razorpay_payment_id);
                        }},
                        modal_error: function(response) {{
                            alert('Payment failed: ' + response.error.description);
                        }},
                        prefill: {{
                            name: 'John Doe',
                            email: 'john.doe@example.com',
                            contact: '8639028233',
                        }},
                        theme: {{
                            color: '#F37254'
                        }}
                    }};
                    var rzp1 = new Razorpay(options);
                    rzp1.open();
                </script>
            </body>
            </html>
            """

            # Save the HTML content to a local file and open it in a pywebview
            self.open_payment_modal(checkout_html)

    def open_payment_modal(self, html_content):
        """
        Function to save the Razorpay payment modal HTML content to a local file
        and open it in the system's pywebview with a custom window size.
        :param html_content: The HTML content that includes the Razorpay checkout script
        """
        # Define the file path for storing the HTML
        file_path = "razorpay_checkout.html"

        # Write the HTML content to the file
        with open(file_path, "w") as file:
            file.write(html_content)

        # Ensure you specify the correct path to the file and open it correctly
        try:
            # Open the Razorpay checkout page inside the pywebview window
            webview.create_window("Razorpay Payment", file_path, width=360, height=640)
            webview.start()
        except Exception as e:
            print(f"Error opening Razorpay payment modal: {e}")

if __name__ == "__main__":
    Kishore().run()
