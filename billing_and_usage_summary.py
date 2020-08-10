import re
import requests
import pandas as pd
import argparse
import pprint
import json
import time
import openpyxl
from datetime import datetime

pp = pprint.PrettyPrinter(indent=4)

parser = argparse.ArgumentParser(description='Parsing arguments for billing and usage summary')
parser.add_argument("--token", required=True, type=str, help="Admin token to use to pull the billing and usage report.")
parser.add_argument("--filename", required=True, type=str, help="Output name for the summarized report.")
parser.add_argument("--realm", required=False, default="us0", type=str, help="Realm where org resides. Defaults to us0.")
parser.add_argument("--month", required=True, type=str, help="Which month's report should be summarized? Example='January'")
args = parser.parse_args()

month_dict = {
    'January': 1,
    'February': 2,
    'March': 3,
    'April': 4,
    'May': 5,
    'June': 6,
    'July': 7,
    'August': 8,
    'September': 9,
    'October': 10,
    'November': 11,
    'December': 12
}
              
TOKEN = args.token
REALM = args.realm
FILENAME = args.filename
try:
    MONTH = month_dict[args.month]
except KeyError as e:
    print("Month '{}' does not exist".format(args.month))
    exit()

def main():
    headers = {
        'x-sf-token': TOKEN,
        'content-type':'application/json'
    }
    url = "https://app.{}.signalfx.com/v2/organization/usage-reports?maxDays=7&maxMonths=12".format(REALM)

    output = None

    try:
        r = requests.get(
            url=url,
            headers=headers)
        r.raise_for_status()
    except requests.exceptions.HTTPError as http_error:
        print("HTTP Error: ", http_error)
        print("Please chek the token and try again.")
        exit()
    except requests.exceptions.ConnectionError as conn_error:
        print("Connection Error: ", conn_error)
        exit()
    except requests.exceptions.RequestException as err:
        print("Error while calling SignalFx API.\n", err)
        exit()

    output = json.loads(r.text)

    report_url = None
    for month in output['Monthly Aggregate Hosts per Hour Reports']:
        if month['MONTH_UTC'] == MONTH:
            report_url = month['SHORTLIVED_URL']['URL']
    if report_url is None:
        print("No report found for {}".format(args.month))
        exit()

    ## DEBUG STUFF
    # report_url = output['Monthly Host per Hour Reports'][0]['SHORTLIVED_URL']['URL']
    # report_url = "/Users/aaronkirk/Development/accenture_report.txt"
    # report_url = "/Users/aaronkirk/Desktop/cloudreach_report.txt"

    try:
        c = pd.read_csv(report_url, sep='\t', header=0)
        print("INFO: This report does not contain a full month's data!")
    except pd.errors.ParserError as e:
        c = pd.read_csv(report_url, sep='\t', header=1, skiprows=[i for i in range(1,8)])

    data = {}
    data['Total'] = ['Total',0,0,0,0]

    pattern = re.compile("^(.*)\s-\s(.*)")
    single_pattern = re.compile("#\s(.*)")
    
    for col in c.columns:
        m = pattern.findall(col)  
        if m is not None and len(m) > 0:
            if len(m[0]) > 1:
                                 
                if m[0][0] in data:
                    pass
                else:
                    data[m[0][0]] = [m[0][0],0,0,0,0]

                if m[0][1] == '# Hosts':
                    data[m[0][0]][1] = round(c[col].mean())
                elif m[0][1] == '# Containers':
                    data[m[0][0]][2] = round(c[col].mean())
                elif m[0][1] == '# Custom Metrics':
                    data[m[0][0]][3] = round(c[col].mean())
                elif m[0][1] == '# High Res Metrics':
                    data[m[0][0]][4] = round(c[col].mean())
        elif m is not None and len(m) == 0:
            total_match = single_pattern.findall(col)
            if total_match is not None and len(total_match) == 1:
                if total_match[0] == 'Hosts':
                    data['Total'][1] = round(c[col].mean())
                elif total_match[0] == 'Containers':
                    data['Total'][2] = round(c[col].mean())
                elif total_match[0] == 'Custom Metrics':
                    data['Total'][3] = round(c[col].mean())
                elif total_match[0] == 'High Res Metrics':
                    data['Total'][4] = round(c[col].mean())

    df = pd.DataFrame(data.values(), columns=['Customer','Hosts','Containers','Custom Metrics','High Res Metrics'])
    df.to_excel(FILENAME)
    
if __name__ == '__main__':
    main()
