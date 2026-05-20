# test_network_diag.py
import httpx
import socket
import traceback

print("=========================================")
print("      NETWORK DIAGNOSTIC LOGS")
print("=========================================")

# 1. DNS check
try:
    print("[1] Resolving DNS for 'api.open-meteo.com'...")
    ip = socket.gethostbyname("api.open-meteo.com")
    print(f"    SUCCESS: ip = {ip}")
except Exception as e:
    print(f"    DNS FAILURE: {e}")

# 2. HTTPX with Open-Meteo
try:
    print("\n[2] Connecting to Open-Meteo weather API...")
    url = "https://api.open-meteo.com/v1/forecast?latitude=33.6844&longitude=73.0479&current=temperature_2m,rain&timezone=Asia%2FKarachi"
    r = httpx.get(url, verify=False, timeout=5)
    print(f"    SUCCESS: status = {r.status_code}")
    print(f"    response snippet: {r.text[:100]}")
except Exception as e:
    print(f"    HTTPX FAILURE: {e}")
    traceback.print_exc()

print("=========================================")
