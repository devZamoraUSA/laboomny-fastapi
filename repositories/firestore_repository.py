import os
import os
import json
from google.cloud import firestore
from google.oauth2 import service_account
from models import FormData


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

        # Convertir 'birthday_date' de 'date' a cadena en formato ISO
        birthday_date = data_dict.get('birthday_date')
        if isinstance(birthday_date, datetime.date):
            data_dict['birthday_date'] = birthday_date.isoformat()

        doc_ref = self.db.collection('form_submissions').document()
        doc_ref.set(data_dict)
        return doc_ref.id
