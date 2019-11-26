#!/usr/bin/env python

"""
This can be used on the csv export from ticktick to convert your tasks
to format needed by taskwarrior.
"""

import argparse
import pandas as pd
import uuid
import json
from datetime import datetime

from pprint import pprint as pp


def parse_args():
    parser = argparse.ArgumentParser(description="A tool to translate ticktick backup csv's to taskwarrior files")
    parser.add_argument('-i', '--input', required=True, help='ticktick backup csv file')
    parser.add_argument('-o', '--output', help='output file for generated taskwarrior json')
    return parser.parse_args()


def dt_convert(tt_dt):

    if not tt_dt:
        return ''

    dt = datetime.strptime(tt_dt, "%Y-%m-%dT%H:%M:%S%z")
    return dt.strftime("%Y%m%dT%H%M%SZ")


def write_to_file(dictlist, path):
    with open(path, 'w') as f:
        for i in range(len(dictlist)):
            f.write(json.dumps(dictlist[i]))
            if i < len(dictlist):
                f.write("\n")


def parse_row(json):

    if json['Status'] == 0:
        status = "pending"
    else:
        status = "completed"

    output_dict = {
        "status": status,
        "uuid": str(uuid.uuid1()),
        "entry": dt_convert(json['Created Time']),
        "description": json['Title'],
    }

    if json['Content']:
        output_dict['annotations'] = [{
            'entry': dt_convert(json['Created Time']),
            'description': json['Content']
        }]

    if json['Priority'] == 5:
        output_dict['priority'] = "H"
    elif json['Priority'] == 3:
        output_dict['priority'] = "M"
    elif json['Priority'] == 1:
        output_dict['priority'] = "L"

    if json['Tags']:
        output_dict['project'] = json['Tags']
    if json['List Name']:
        output_dict['tags'] = [json['List Name']]

    return output_dict


def main():
    args = parse_args()
    input_csv = pd.read_csv(args.input, keep_default_na=False)
    test_dict = input_csv.iloc[0].to_dict()

    output_dict = []
    for i in range(len(input_csv)):
        row = input_csv.iloc[i].to_dict()
        output_dict.append(parse_row(row))

    if not args.output:
        args.output = args.input.replace("csv", "json")

    write_to_file(output_dict, args.output)

if __name__ == "__main__":
    main()
