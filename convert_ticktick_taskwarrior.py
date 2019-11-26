#!/usr/bin/env python

"""
This can be used on the csv export from ticktick to convert your tasks
to format needed by taskwarrior.
"""

import argparse
import pandas as pd
import uuid
from datetime import datetime

from pprint import pprint as pp


def parse_args():
    parser = argparse.ArgumentParser(description="A tool to translate ticktick backup csv's to taskwarrior files")
    parser.add_argument('-i', '--input', required=True, help='ticktick backup csv file')
    return parser.parse_args()


def dt_convert(tt_dt):

    if not tt_dt:
        return ''

    dt = datetime.strptime(tt_dt, "%Y-%m-%dT%H:%M:%S%z")
    return dt.strftime("%Y%M%dT%H%M%SZ")


def parse_row(json):

    if json['Status'] == 0:
        status = "Pending"
    else:
        status = "Completed"

    output_dict = {
        "status": status,
        "uuid": str(uuid.uuid1().hex),
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

    pp(output_dict)
    return output_dict


if __name__ == "__main__":
    main()
