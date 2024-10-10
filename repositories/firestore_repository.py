import os
import json
import datetime
from google.cloud import firestore
from google.oauth2 import service_account
from models import FormData
from datetime import date, datetime


class FirestoreRepository:
    def __init__(self):
        credentials_info = os.getenv("GOOGLE_CREDENTIALS")
        if not credentials_info:
            raise ValueError("Missing Google credentials")

        credentials_dict = json.loads(credentials_info)
        credentials = service_account.Credentials.from_service_account_info(credentials_dict)
        self.db = firestore.Client(credentials=credentials)

    def save(self, data: FormData):
        data_dict = data.dict()
        # Convertir 'birthday_date' y 'submission_datetime' a cadenas si es necesario
        birthday_date_value = data_dict.get('birthday_date')
        if isinstance(birthday_date_value, date):
            data_dict['birthday_date'] = birthday_date_value.isoformat()

        submission_datetime_value = data_dict.get('submission_datetime')
        if isinstance(submission_datetime_value, datetime):
            data_dict['submission_datetime'] = submission_datetime_value.isoformat()

        # Añadir campo 'paid' con valor False por defecto
        data_dict['paid'] = False

        # Crear un nuevo documento con ID automático
        doc_ref = self.db.collection('form_submissions').document()
        doc_ref.set(data_dict)
        return doc_ref.id

    def update_payment_status(self, document_id: str, paid: bool):
        doc_ref = self.db.collection('form_submissions').document(document_id)
        doc_ref.update({'paid': paid})

    def get_form_data(self, document_id: str):
        doc_ref = self.db.collection('form_submissions').document(document_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        else:
            return None
