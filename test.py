import requests
import base64

# === Configuration ===
API_URL = "http://127.0.0.1:8000/api/"
QUESTION = "Should I use gpt-4o-mini which AI proxy supports, or gpt3.5 turbo?"
IMAGE_PATH = "project-tds-virtual-ta-q1.webp"  # Replace with your image path if needed (e.g. "example.webp")
# =====================

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Prepare payload
payload = {
    "question": QUESTION,
    "image": encode_image(IMAGE_PATH) if IMAGE_PATH else None
}

# Send POST request
response = requests.post(API_URL, json=payload)

# Output
if response.status_code == 200:
    data = response.json()
    print("\n✅ Answer:")
    print(data["answer"])
    if data["links"]:
        print("\n🔗 Related Links:")
        for link in data["links"]:
            print(f"- {link['text']}: {link['url']}")
else:
    print(f"❌ Error {response.status_code}: {response.text}")

# import requests
# import base64

# # Read and encode the image as base64
# with open("C:\\Users\\Admin\\Documents\\iitm tds project\\project-tds-virtual-ta-q1.webp", "rb") as image_file:
#     image_base64 = base64.b64encode(image_file.read()).decode('utf-8')

# url = "http://127.0.0.1:8000/api/"
# payload = {
#     "question": "Should I use gpt-3.5 instead of gpt-4o-mini in the AI proxy?",
#     "image": image_base64
# }

# response = requests.post(url, json=payload)

# print("Status Code:", response.status_code)
# print("Response Text:", response.text)

