import base64

with open("token.pickle", "rb") as f:
    encoded = base64.b64encode(f.read()).decode("utf-8")

with open("token.pickle.b64", "w") as f:
    f.write(encoded)

print("✅ Base64 file saved as token.pickle.b64")
