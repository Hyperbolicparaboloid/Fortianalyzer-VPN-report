import requests
import json
import time

import tqdm
from termcolor import colored
import os
from datetime import datetime, timedelta, date

os.system('color')
FORTI = "https://FortianalyzerIP/jsonrpc"
ADOM_NAME = "root"
token="API-Token"

headers={"Content-Type": "application/json"}

body1 = {
    "method": "exec",
    "params": [
        {"url": "/sys/login/user","data":{ "user":"API_usr","passwd":"PASSWORD"}}
    ],
    "id": 1,
}

requests.packages.urllib3.disable_warnings()
session_resp = requests.post(FORTI,headers=headers, data=json.dumps(body1), verify=False)
session_resp_json = session_resp.json()

session_cookie = session_resp_json["session"]

print(colored("""
 /$$    /$$ /$$$$$$$  /$$   /$$       /$$$$$$$                                            /$$    
| $$   | $$| $$__  $$| $$$ | $$      | $$__  $$                                          | $$    
| $$   | $$| $$  \ $$| $$$$| $$      | $$  \ $$  /$$$$$$   /$$$$$$   /$$$$$$   /$$$$$$  /$$$$$$  
|  $$ / $$/| $$$$$$$/| $$ $$ $$      | $$$$$$$/ /$$__  $$ /$$__  $$ /$$__  $$ /$$__  $$|_  $$_/  
 \  $$ $$/ | $$____/ | $$  $$$$      | $$__  $$| $$$$$$$$| $$  \ $$| $$  \ $$| $$  \__/  | $$    
  \  $$$/  | $$      | $$\  $$$      | $$  \ $$| $$_____/| $$  | $$| $$  | $$| $$        | $$ /$$
   \  $/   | $$      | $$ \  $$      | $$  | $$|  $$$$$$$| $$$$$$$/|  $$$$$$/| $$        |  $$$$/
    \_/    |__/      |__/  \__/      |__/  |__/ \_______/| $$____/  \______/ |__/         \___/  
                                                         | $$                                    
                                                         | $$      ᵒᵐᵃʳ ᵐᵃⁿˢᵒᵘʳ                              
                                                         |__/                                    
""",'blue'))




username=input(colored("input username to search for: ",'green'))
start_time=input(colored("please input the start time in the following format YYYY/MM/DD: ",'green'))
end_time=input(colored("please input the end time in the following format YYYY/MM/DD: ",'green'))


start_date = datetime.strptime(start_time, "%Y/%m/%d")
end_date = datetime.strptime(end_time, "%Y/%m/%d")

current_date = start_date
counter=0

while current_date <= end_date:
    body3 = {
        "id": "3",
        "jsonrpc": "2.0",
        "method": "add",
        "params": [{"apiver": 3,"schedule-param": { "device": "fortigate device name","filter":[ {"name": "xauthuser","opcode":0, "value":f"{username}"}],"layout-id":"9","time-period":"other","period-end": "23:59:00 "+f"{current_date.strftime('%Y/%m/%d')}","period-start": "00:00:00 "+f"{current_date.strftime('%Y/%m/%d')}"} , "url": f"/report/adom/{ADOM_NAME}/run"}],
        "session": session_cookie,
    }
    results_resp = requests.post(FORTI, data=json.dumps(body3),verify=False)
    results_resp_json = results_resp.json()
    
    tid = results_resp_json["result"]["tid"]


    progress=0
    pbar = tqdm.tqdm(desc="Progress", total=100,colour='green')
   
    while progress < 100:
        now_progress=progress
        body4 = {
            "id": "3",
            "jsonrpc": "2.0",
            "method": "get",
            "params": [
                {"apiver": 3,"url": f"/report/adom/{ADOM_NAME}/run/{tid}"}],
            "session": session_cookie,
        }
        status_resp = requests.post(FORTI, data=json.dumps(body4), verify=False)
        status_resp_json=status_resp.json()
        try:
            progress=status_resp_json["result"]["progress-percent"]
            if progress!=now_progress:
                pbar.update(progress-pbar.n)
            else: pass
        except KeyError:
            pass
    pbar.close()



    print(colored("Report completed\n",'green'))

    result=0

    body4 = {
        "id": "3",
        "jsonrpc": "2.0",
        "method": "get",
        "params": [{"apiver": 3,"data-type":"text", "format":"csv" ,"url": f"/report/adom/{ADOM_NAME}/reports/data/{tid}"}],
        "session": session_cookie,
    }
    print(colored("Please wait fetching report\n",'green'))
    time.sleep(8)

    results2_resp = requests.post(FORTI, data=json.dumps(body4),verify=False)
    results2_resp_json = results2_resp.json()
    res=results2_resp_json
    print(colored("report details: " + results2_resp_json['result']['data'],'green'))

    today=date.today()
    with open(f"{username}-"+str(today)+"-VPN-Duration-report.txt","a") as file:
        try:
            file.write(res["result"]["data"])
        except UnicodeEncodeError:
            print(colored("no data found for the specifed duration or user...",'red'))
    current_date += timedelta(days=1)
    counter=counter+1
    if counter >= 20:
        print(colored("!!!RUNNING REPORTS FOR PERIODS LONGER THAN 20 DAYS IS NOT PERMITTED!!!",'red'))
        break

input(colored("Press any key to esc.....",'magenta'))