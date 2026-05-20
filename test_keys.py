import os
from google import genai
keys = ['AIzaSyBZLSf7JA4XGj-qmCXG9rosMAy_eocLnxI', 'AIzaSyCbmWT1wY4GBjYPbMgEpNOQU9QjIa6LZ_4', 'AIzaSyBppj2ymnVjjohJg3qjBKDnFsry_zGeQPM']
for i, k in enumerate(keys):
    try:
        client = genai.Client(api_key=k)
        resp = client.models.generate_content(model='models/gemini-2.5-flash', contents='hello')
        print(f'Key {i+1}: WORKING')
    except Exception as e:
        print(f'Key {i+1}: ERROR - {str(e)[:100]}')
