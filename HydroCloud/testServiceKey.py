from google.cloud import firestore

def initialize_firestore():
    """
    Initialize Firestore using the service account key.
    """
    try:
        # Replace 'serviceAccountKey.json' with the path to your Firebase service account key file
        db = firestore.Client.from_service_account_json("/home/tcar5787/APIkeys/hydrometer/serviceAccountKey.json")
        print("Successfully connected to Firestore.")
        return db
    except Exception as e:
        print(f"Error connecting to Firestore: {e}")
        return None

def test_firestore_connection(db):
    """
    Test Firestore by writing and reading data.
    """
    try:
        # Reference a test collection
        test_collection = db.collection("test_collection")

        # Write a test document
        test_data = {"message": "Hello, Firestore!", "timestamp": firestore.SERVER_TIMESTAMP}
        doc_ref = test_collection.document("test_document")
        doc_ref.set(test_data)
        print("Test document written to Firestore.")

        # Read back the test document
        result = doc_ref.get()
        if result.exists:
            print("Test document read successfully:", result.to_dict())
        else:
            print("Test document does not exist.")

    except Exception as e:
        print(f"Error testing Firestore: {e}")

if __name__ == "__main__":
    # Initialize Firestore
    db = initialize_firestore()

    # If initialization is successful, run the test
    if db:
        test_firestore_connection(db)