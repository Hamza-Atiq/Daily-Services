"""
Seed Firebase Firestore with mock provider data.
Can also be run standalone to populate the database.
"""

import json
import os


_SEED_FILE = os.path.join(os.path.dirname(__file__), "providers_seed.json")


def seed_providers(db):
    """Seed the Firestore 'providers' collection with mock data if it's empty."""
    try:
        # Check if providers already exist
        existing = db.collection("providers").limit(1).get()
        if len(list(existing)) > 0:
            print("  Providers collection already has data, skipping seed.")
            return

        # Load seed data
        with open(_SEED_FILE, "r", encoding="utf-8") as f:
            providers = json.load(f)

        # Upload each provider
        for provider in providers:
            doc_id = provider.get("id", None)
            if doc_id:
                db.collection("providers").document(doc_id).set(provider)
            else:
                db.collection("providers").add(provider)

        print(f"  ✅ Seeded {len(providers)} providers to Firestore.")
    except Exception as e:
        print(f"  ⚠️ Could not seed providers: {e}")


def seed_locations(db):
    """Seed the Firestore 'locations' collection with Islamabad sector data."""
    try:
        locations_file = os.path.join(os.path.dirname(__file__), "locations.json")
        with open(locations_file, "r", encoding="utf-8") as f:
            locations = json.load(f)

        db.collection("config").document("locations").set(locations)
        print(f"  ✅ Seeded {len(locations['sectors'])} sectors to Firestore.")
    except Exception as e:
        print(f"  ⚠️ Could not seed locations: {e}")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from api.core.firebase import get_db
    db = get_db()
    seed_providers(db)
    seed_locations(db)
    print("Done!")
