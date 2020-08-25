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
parser.add_argument("--input_file", required=True, type=str, help="Input file downloaded from SignalFx")
parser.add_argument("--output_file", required=True, type=str, help="Output name for the summarized report.")

args = parser.parse_args()

INPUT_FILE = args.input_file
OUTPUT_FILE = args.output_file

def main():

    ## DEBUG STUFF
    # report_url = output['Monthly Host per Hour Reports'][0]['SHORTLIVED_URL']['URL']
    # report_url = "/Users/aaronkirk/Development/accenture_report.txt"
    # report_url = "/Users/aaronkirk/Desktop/cloudreach_report.txt"

    try:
        c = pd.read_csv(INPUT_FILE, sep='\t', header=0)
        print("INFO: This report does not contain a full month's data!")
    except pd.errors.ParserError as e:
        c = pd.read_csv(INPUT_FILE, sep='\t', header=1, skiprows=[i for i in range(1,8)])

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
    df.to_excel(OUTPUT_FILE)
    
if __name__ == '__main__':
    main()
