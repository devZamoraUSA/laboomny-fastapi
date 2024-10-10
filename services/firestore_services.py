from repositories.firestore_repository import FirestoreRepository
from models import FormData

class FirestoreService:
    def __init__(self, repository: FirestoreRepository):
        self.repository = repository

    def save_form_data(self, data: FormData):
        # Lógica adicional si es necesaria
        return self.repository.save(data)

# Dependency Injection
def get_firestore_service():
    repository = FirestoreRepository()
    return FirestoreService(repository)
