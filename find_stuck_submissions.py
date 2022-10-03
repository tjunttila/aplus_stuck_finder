#!/usr/bin/python3

"""
A small tool for finding "Initialized" submissions in an A+ course.
Author: Tommi Junttila
"""

import argparse
import datetime
import sys
import time
import requests
import yaml
from dateutil.parser import parse as timeparser


def api_get_url_json(url, access_token, params=None):
    """
    Fetch a JSON file from the A+ API.
    """
    api_headers = {'Content-type': 'application/json',
                   'Authorization': f'Token {access_token}'}
    if params is None:
        params = {}
    response = requests.get(url, headers=api_headers, **params)
    if response.status_code != 200:
        print(f'Requested: {response.url}')
        print(f'Response: {response}')
        print(f'Reason: {response.reason}')
        if response.status_code >= 300 and response.status_code < 400:
            print("Did you set the API URL correctly?")
        elif response.status_code == 401:
            print("Did you set the API Access token correctly?")
        elif response.status_code == 404:
            print("Are the API URL and the exercise ID correct?")
        sys.exit(1)
    return response.json()


def api_get_paginated_json(url, access_token, params=None):
    """
    Fetch a paginated JSON file from the A+ API.
    """
    results = []
    while url is not None:
        data = api_get_url_json(url, access_token, params)
        results.extend(data['results'])
        url = data['next']
    return results


def find_stuck_submissions(access_token, api_url, course_id, since: int):
    """
    Find all stuck (not "ready" or "rejected) submissions in an A+ course.
    Return the list of their "inspect" URLs.
    """

    def api_get_json(url, params=None):
        """Get a JSON file from the A+ API."""
        return api_get_url_json(url, access_token, params)

    def api_get_paginated(url, params=None):
        """Get a paginated JSON file from the A+ API."""
        return api_get_paginated_json(url, access_token, params)

    now_time = datetime.datetime.astimezone(datetime.datetime.now())

    print("Fetching the exercises index")
    api_exercises_url = f'{api_url}/courses/{course_id}/exercises'
    exercises_json = api_get_paginated(api_exercises_url)
    time.sleep(1)
    stuck_urls = []
    for round_json in exercises_json:
        print(f'Scanning round: {round_json["display_name"]}')
        for exercise_json in round_json['exercises']:
            exercise_json = api_get_json(exercise_json['url'])
            exercise_name = exercise_json['display_name']
            print(f'  Scanning exercise: {exercise_name}')
            submissions_json = api_get_paginated(exercise_json['submissions'])
            for submission_json in submissions_json:
                if submission_json['grade'] != 0:
                    continue
                submission_time = timeparser(submission_json['submission_time'])
                if (now_time - submission_time).days >= since:
                    continue
                submission_json = api_get_json(submission_json['url'])
                time.sleep(0.5)
                if submission_json['status'] in ['ready', 'rejected']:
                    continue
                inspect_url = submission_json['html_url']+'inspect/'
                stuck_urls.append(inspect_url)
                # print(inspect_url)
                # print(submission_json)
    return stuck_urls


def main():
    """
    The main function for command line use.
    """
    description = ('Find all recent submissions in an A+ course that are '
                   'not "ready" or "rejected".')
    argp = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=description)
    argp.add_argument('--since', type=int, default=1, metavar='S',
                      help=('only consider submissions that are less than '
                            'S days old'))
    argp.add_argument('--config', default='find_stuck_submissions.yml',
                      metavar='C',
                      help=('The config YAML file with the access token and '
                            'the course id'))
    argp.add_argument('--urls-file', default='stuck_submissions.txt',
                      metavar='F',
                      help=('The "inspect" URLs of the stuck submissions '
                            'will be output in this file'))
    args = argp.parse_args()

    # Read the configutation file
    with open(args.config, 'r', encoding='utf-8') as config_file:
        config = yaml.safe_load(config_file)

    # Get the relevant information from the config file
    api_url = config['api-url']
    access_token = config['access-token']
    course_id = config['course-id']
    if not isinstance(course_id, int):
        argp.error('The course-id in the config YAMl file should be an integer')

    # Find the stuck submissions and get their "inspect" URLS
    stuck_urls = find_stuck_submissions(access_token, api_url, course_id,
                                        args.since)

    # Write the "inspect" URLS in a file
    with open(args.urls_file, 'w', encoding='utf-8') as urls_fh:
        for stuck_url in stuck_urls:
            urls_fh.write(stuck_url+'\n')

    # Give the user a way to continue to manual resubmission
    print(f"""Found {len(stuck_urls)} possibly stuck submissions.
Their URLs are listed in "{args.urls_file}".
In Linux systems, run
  cat {args.urls_file} | xargs firefox
to lauch Firefox with a tab for each of them.""")


if __name__ == "__main__":
    main()
