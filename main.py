from fastapi import FastAPI, Depends, HTTPException, Request
from services.firestore_services import FirestoreService, get_firestore_service
from models import FormData
import stripe
import os
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from dotenv import load_dotenv  # Importa load_dotenv

load_dotenv()
app = FastAPI()

# Configurar la clave secreta de Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Configurar la API Key de Brevo
brevo_api_key = os.getenv("BREVO_API_KEY")
if not brevo_api_key:
    raise ValueError("La variable de entorno BREVO_API_KEY no está configurada.")

# Configurar la instancia de la API de Brevo
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = brevo_api_key
api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

@app.get("/")
async def root():
    return {"message": "API is working correctly"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Mapeo de opciones del formulario a IDs de precio de Stripe
PRICE_MAPPING = {
    "VIP Package": "price_1Q8SFtP5FOj6UOuafVjGPYJB",
    "Standard Package": "price_1Q8SFPP5FOj6UOuarOrpKghL",
    # Agrega más opciones si es necesario
}

@app.post("/submit-form")
async def submit_form(data: FormData, firestore_service: FirestoreService = Depends(get_firestore_service)):
    try:
        # Mapeo de opciones a IDs de precios de Stripe
        PRICE_MAPPING = {
            "VIP Package": "price_1Q8SFtP5FOj6UOuafVjGPYJB",
            "Standard Package": "price_1Q8SFPP5FOj6UOuarOrpKghL",
            # Agrega más opciones si es necesario
        }

        # Obtener el ID de precio basado en la opción seleccionada
        selected_option = data.options
        price_id = PRICE_MAPPING.get(selected_option)

        if not price_id:
            raise HTTPException(status_code=400, detail="Opción de paquete inválida seleccionada.")

        # Guardar datos en Firestore y obtener el ID del documento
        document_id = firestore_service.save_form_data(data)

        # Crear una sesión de Stripe Checkout
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{data.success_url}?status=success&session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{data.cancel_url}?status=cancel",
            client_reference_id=document_id,
            customer_email=data.email
        )

        return {"status": "success", "sessionId": session.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Función para enviar correo de confirmación
def send_confirmation_email(to_email):
    subject = "Confirmación de Pago - LaBoom"
    sender = {"name": "LaBoom", "email": "marcoa.sedeno@zamorausa.com"}
    to = [{"email": to_email}]
    html_content = "<strong>Gracias por tu pago. ¡Esperamos celebrar contigo!</strong>"
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to,
        sender=sender,
        subject=subject,
        html_content=html_content
    )
    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        print(f"Email sent to {to_email}. Message ID: {api_response.message_id}")
    except ApiException as e:
        print(f"Error sending email to {to_email}: {e}")


# Endpoint para manejar webhooks de Stripe
@app.post("/webhook")
async def stripe_webhook(request: Request, firestore_service: FirestoreService = Depends(get_firestore_service)):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        # Payload inválido
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        # Firma inválida
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Manejar el evento
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        client_reference_id = session.get('client_reference_id')

        # Actualizar el estado del pago en Firestore
        firestore_service.update_payment_status(client_reference_id, True)

        # Obtener datos del usuario desde Firestore
        form_data = firestore_service.get_form_data(client_reference_id)
        if form_data:
            user_email = form_data.get('email')

            # Enviar correo de confirmación
            send_confirmation_email(user_email)
        else:
            print(f"No se encontró el documento con ID {client_reference_id}")
    else:
        # Manejar otros eventos si es necesario
        pass

    return {"status": "success"}
