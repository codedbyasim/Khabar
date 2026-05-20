# check_resources_supabase.py
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))

from firestore_db import KhabarFirestore

db = KhabarFirestore()
resources = db.get_resources()

print("==================================================")
print("     LIVE SUPABASE RESOURCE TABLE CONTENTS")
print("==================================================")
if not resources:
    print("[-] No resources found in the 'resources' table!")
else:
    print(f"[+] Found {len(resources)} resource records:\n")
    for r in resources:
        print(f" - ID: {r['resource_id']}")
        print(f"   Name: {r['name']}")
        print(f"   Type: {r['resource_type']}")
        print(f"   Quantity Available: {r['quantity_available']}")
        print(f"   Status: {r['status']}")
        print("-" * 30)
print("==================================================")
