import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

# Configuration (should be moved to env variables in production)
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "noreply@example.com"
SMTP_PASSWORD = "password"

async def send_order_confirmation(email: str, order_data: Dict):
    """Send order confirmation email (ID 889)"""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Order Confirmation - {order_data['order_number']}"
        msg["From"] = SMTP_USER
        msg["To"] = email
        
        # Create HTML content
        html = f"""
        <html>
          <body>
            <h1>Thank you for your order!</h1>
            <p>Order Number: <strong>{order_data['order_number']}</strong></p>
            <p>Order Date: {order_data['created_at']}</p>
            
            <h2>Order Summary</h2>
            <table>
              <tr>
                <th>Product</th>
                <th>Quantity</th>
                <th>Price</th>
                <th>Total</th>
              </tr>
        """
        
        for item in order_data['items']:
            html += f"""
              <tr>
                <td>{item['product_title']}</td>
                <td>{item['quantity']}</td>
                <td>€{item['unit_price']:.2f}</td>
                <td>€{item['total_price']:.2f}</td>
              </tr>
            """
        
        html += f"""
            </table>
            
            <h3>Totals</h3>
            <p>Subtotal: €{order_data['subtotal']:.2f}</p>
            <p>Shipping: €{order_data['shipping_cost']:.2f}</p>
            <p>VAT: €{order_data['tax_amount']:.2f}</p>
            <p><strong>Total: €{order_data['total_amount']:.2f}</strong></p>
            
            <h3>Shipping Address</h3>
            <p>
              {order_data['shipping_address']['first_name']} {order_data['shipping_address']['last_name']}<br>
              {order_data['shipping_address']['address_line1']}<br>
              {order_data['shipping_address']['address_line2']}<br>
              {order_data['shipping_address']['postal_code']} {order_data['shipping_address']['city']}<br>
              {order_data['shipping_address']['country']}
            </p>
            
            <p>Your order has been received and is being processed.</p>
          </body>
        </html>
        """
        
        part = MIMEText(html, "html")
        msg.attach(part)
        
        # Send email (commented out for development)
        # with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        #     server.starttls()
        #     server.login(SMTP_USER, SMTP_PASSWORD)
        #     server.sendmail(SMTP_USER, email, msg.as_string())
        
        logger.info(f"Order confirmation email would be sent to {email}")
        
    except Exception as e:
        logger.error(f"Failed to send email: {e}")