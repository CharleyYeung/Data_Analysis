import os
import json
import requests
from datetime import datetime

def fetch_and_save_tfl_status():
    # GET API KEY FROM ENVIRONMENT VARIABLE
    tfl_key = os.environ.get("TFL_APP_KEY")

    modes = "tube,elizabeth-line,overground,dlr,tram"
    
    # URL DECISION: IF KEY EXISTS, USE IT; OTHERWISE, USE PUBLIC API
    if tfl_key:
        print("🔑 Detecting TFL_APP_KEY, fetching with credentials...")
        url = f"https://api.tfl.gov.uk/line/mode/{modes}/status?app_key={tfl_key}"
    else:
        print("🌐 No API key detected. Fetching via Public Anonymous API...")
        url = f"https://api.tfl.gov.uk/line/mode/{modes}/status"
        
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        lines_data = response.json()
    except Exception as e:
        print(f"Error fetching data from TfL: {e}")
        return

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    output = {}
    disrupted_records = []

    for line in lines_data:
        line_name = line.get("name")
        line_statuses = line.get("lineStatuses", [])
        
        is_disrupted = False
        reason = "Normal Operation"
        status_desc = "Good Service"
        
        if line_statuses:
            status_desc = line_statuses[0].get("statusSeverityDescription", "Good Service")
            if status_desc != "Good Service":
                is_disrupted = True
                reason = line_statuses[0].get("reason", status_desc)
                
        # PRIMARY OUTPUT: JSON FILE FOR FRONTEND
        output[line_name] = {
            "is_disrupted": is_disrupted,
            "reason": reason
        }

        # DISRUPTED RECORDS: FOR CSV LOGGING
        if is_disrupted:
            # CLEAN REASON: REMOVE NEWLINES AND COMMAS TO AVOID CSV ISSUES
            clean_reason = reason.replace("\n", " ").replace(",", " ")
            disrupted_records.append([current_time, line_name, clean_reason, "True"])

    script_dir = os.path.dirname(os.path.abspath(__file__))

    # ASSURE 100% RELIABILITY: ALWAYS WRITE TO A LOCAL FILE, NO MATTER WHAT
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, "status.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)
        
    # ENRICHED LOGGING: ONLY APPEND DISRUPTED EVENTS TO HISTORY, KEEPING GOOD SERVICE OUT OF THE LOG
    if disrupted_records:
        csv_path = os.path.join(script_dir, "disruption_history.csv")
        with open(csv_path, "a", encoding="utf-8-sig") as f:
            for record in disrupted_records:
                f.write(",".join(record) + "\n")
        print(f"📈 Logged {len(disrupted_records)} disruption events to history database.")
    else:
        print("🟢 All lines running smoothly. No disruption logged.")

if __name__ == "__main__":
    fetch_and_save_tfl_status()