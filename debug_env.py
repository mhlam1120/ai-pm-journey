import sys
import os
import importlib.util

print("--- 🕵️ DETECTIVE MODE ---")

# 1. CHECK FOR SHADOWS (The Silent Killer)
files = os.listdir(".")
if "langchain.py" in files or "langchain" in files:
    print("❌ CRITICAL ERROR FOUND!")
    print("You have a file or folder named 'langchain' in your project.")
    print("Python is trying to read THIS instead of the library.")
    print("👉 ACTION: Rename it to something else (e.g., 'my_langchain_test').")
    exit()
else:
    print("✅ No shadow files found.")

# 2. CHECK PYTHON INTERPRETER
# This tells us WHICH python is actually running this script.
print(f"\n🐍 Python Executable: {sys.executable}")
if "venv" not in sys.executable:
    print("⚠️ WARNING: You are NOT running inside the 'venv' virtual environment!")
    print("   This script is running on your global system Python.")
    print("   If you installed libraries in 'venv', this script cannot see them.")
else:
    print("✅ Running inside 'venv'.")

# 3. CHECK PACKAGES
print("\n--- 📦 Checking Installed Packages ---")


def check_package(name):
    try:
        spec = importlib.util.find_spec(name)
        if spec is None:
            print(f"❌ {name}: NOT FOUND")
        else:
            print(f"✅ {name}: Found at {spec.origin}")
    except Exception as e:
        print(f"❌ {name}: Error finding spec ({e})")


check_package("langchain")
check_package("langchain.chains")
check_package("langchain_community")

# 4. TEST IMPORT
print("\n--- 🔗 Attempting Real Import ---")
try:
    from langchain.chains import RetrievalQA
    print("🎉 SUCCESS! The import works.")
except Exception as e:
    print(f"💥 FAILURE: {e}")

print("\n--- 🏁 END REPORT ---")
