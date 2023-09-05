import firebase_admin
from firebase_admin import credentials, auth, db



class FirebaseController:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseController, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.cred = credentials.Certificate("firebase-private-key.json")
            self.app = firebase_admin.initialize_app(
                self.cred,
                {"databaseURL": "https://......firebaseio.com/"},
            )
            self.db = db
            self.ref = self.db.reference("/emails")
            self._initialized = True
    
    def authorize_with_email(self, email, password):
        try:
            user = auth.get_user_by_email(email)
            if user:
                pass
        except auth.UserNotFoundError:
            print(f"No user found for the provided email: {email}")
            return None
        except Exception as e:
            print(f"An error occurred during authorization: {e}")
            return None
    
    def save_email(self, data):
        try:
            existing_data = self.ref.get()
            if existing_data is None:
                self.ref.push(data)
            else:
                for key, value in existing_data.items():
                    if value == data:
                        self.ref.child(key).update(data)
                        return
                self.ref.push(data)
        except Exception as e:
            print(f"An error occurred during writing data: {e}")
            return False

    def is_email_sent(self, msg_id):
        try:
            existing_data = self.ref.get()
            if existing_data is not None:
                for value in existing_data.values():
                    if str(msg_id) == str(value.get("msg_id")):
                        return True  # msg sent
            return False  # msg not sent
        except Exception as e:
            print(f"An error occurred during checking if email sent: {e}")
            return False
    
    def get_history_id(self):
        try:
            history_ref = self.db.reference("/history_id")
            history_id = history_ref.get()

            if history_id is not None:
                return history_id
            else:
                return None
        except Exception as e:
            print(f"An error occurred during fetching history_id: {e}")
            return None
    
    def set_history_id(self, history_id):
        try:
            history_ref = self.db.reference("/history_id")
            history_ref.set(history_id)
            return True
        except Exception as e:
            print(f"An error occurred during setting history_id: {e}")
            return False
    
