from repositories.firestore_repository import FirestoreRepository
from models import FormData

class FirestoreService:
    def __init__(self, repository: FirestoreRepository):
        self.repository = repository

    def save_form_data(self, data: FormData):
        return self.repository.save(data)

    def update_payment_status(self, document_id: str, paid: bool):
        self.repository.update_payment_status(document_id, paid)

    def get_form_data(self, document_id: str):
        return self.repository.get_form_data(document_id)

# Dependency Injection
def get_firestore_service():
    repository = FirestoreRepository()
    return FirestoreService(repository)
