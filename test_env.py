"""測試環境變數載入"""
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("環境變數測試")
print("=" * 60)

env_vars = {
    'META_APP_ID': os.getenv('META_APP_ID'),
    'META_APP_SECRET': os.getenv('META_APP_SECRET'),
    'META_ACCOUNT_ID': os.getenv('META_ACCOUNT_ID'),
    'WC_URL': os.getenv('WC_URL'),
    'WC_CONSUMER_KEY': os.getenv('WC_CONSUMER_KEY'),
}

for key, value in env_vars.items():
    if value:
        if 'SECRET' in key or 'KEY' in key:
            print(f"✅ {key}: {value[:10]}... (已隱藏)")
        else:
            print(f"✅ {key}: {value}")
    else:
        print(f"❌ {key}: 未設定")

print("=" * 60)
