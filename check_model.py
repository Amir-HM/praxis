import replicate
import os
from dotenv import load_dotenv

load_dotenv()

model_name = "lucataco/deepseek-ocr"
print(f"Checking model: {model_name}")

try:
    model = replicate.models.get(model_name)
    print(f"✅ Model found: {model.owner}/{model.name}")
    if model.latest_version:
        print(f"✅ Latest version: {model.latest_version.id}")
    else:
        print("❌ No latest version found")
        
    # List versions
    print("\nRecent versions:")
    for v in model.versions.list()[:3]:
        print(f" - {v.id} ({v.created_at})")
        
except Exception as e:
    print(f"❌ Error: {e}")
