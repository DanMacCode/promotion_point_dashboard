import os
import requests
import subprocess
import sys
from dotenv import load_dotenv


os.chdir(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()
# List of scripts in order of execution
scripts = [
    "scripts/cleanup_folders.py",
    "scripts/scrape_pdfs.py",
    "scripts/pdf_to_txt.py",
    "scripts/rename_txts.py",
    "scripts/cleanup_old_txts.py",
    "scripts/txt_to_csv.py",
    "scripts/compile_master_dataset.py"
]


print("Starting Monthly Promotion Point Update Pipeline...\n")

for script in scripts:
    print(f"Running {script}...")
    result = subprocess.run(
    [sys.executable, script],
    capture_output=True,
    text=True,
    cwd=os.path.dirname(__file__)  # Ensures all scripts run from the correct project root
)



    if result.returncode != 0:
        print(f"Error running {script}:\n{result.stderr}")
        break  # Stop the pipeline if any script fails
    else:
        print(f"Completed {script}\n{result.stdout}\n")

print("Pipeline complete see above to see it there were any error because this line doesnt tell you if it completed successfully.")


def git_push():
    try:
        subprocess.run(["git", "add", "data/master/master_promotion_data.csv"], check=True)
        subprocess.run(["git", "commit", "-m", "Monthly update to master CSV"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("CSV committed and pushed to GitHub.")
    except subprocess.CalledProcessError as e:
        print(f"Git push failed: {e}")



import requests

def send_push_notification():
    key = os.getenv("SIMPLEPUSH_KEY")
    if not key:
        print("SIMPLEPUSH_KEY not found.")
        return

    payload = {
        "key": key,
        "title": "Promotion Update Complete",
        "message": "Promotion Point Dashboard updated and pushed to GitHub."
    }

    response = requests.post("https://api.simplepush.io/send", data=payload)

    if response.status_code == 200:
        print("SimplePush notification sent.")
    else:
        print(f"Failed to send push notification: {response.text}")


git_push()
send_push_notification()