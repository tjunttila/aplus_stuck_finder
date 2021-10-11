#!/usr/bin/python3

"""
A small tool for finding "Initialized" submissions in an A+ course.
Author: Tommi Junttila
"""

import argparse
import sys
import time
import requests
import yaml


def api_get_url_json(url, access_token, params=None):
    """
    Fetch a JSON file from the A+ API.
    """
    api_headers = {'Content-type': 'application/json',
                   'Authorization': f'Token {access_token}'}
    if params is None:
        params = {}
    response = requests.get(url, headers=api_headers, params={**params, 'format': 'json'})
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


def find_stuck_submissions(access_token, api_url, course_id):
    """
    Find all stuck (not "ready" or "rejected) submissions in an A+ course.
    Return the list of their "inspect" URLs.
    """

    def api_get_json(url, params=None):
        """Get a JSON file from the A+ API."""
        return api_get_url_json(url, access_token, params)

    print("Fetching the exercises index")
    api_exercises_url = f'{api_url}/courses/{course_id}/exercises'
    exercises_json = api_get_json(api_exercises_url)
    time.sleep(1)

    stuck_urls = []
    for round_json in exercises_json['results']:
        print(f'Scanning round: {round_json["display_name"]}')
        for exercise_json in round_json['exercises']:
            exercise_id = exercise_json['id']
            exercise_name = exercise_json['display_name']
            exercise_html = exercise_json['html_url']
            print(f'  Scanning exercise: {exercise_name}')
            submissions_json = api_get_json(
                f'{api_url}/courses/{course_id}/submissiondata/?exercise_id={exercise_id}',
                {'best': 'no'})
            for submission_json in submissions_json:
                submission_id = submission_json['SubmissionID']
                submission_status = submission_json['Status']
                inspect_url = f'{exercise_html}/submissions/{submission_id}/inspect/'
                if submission_status not in ['ready', 'rejected']:
                    stuck_urls.append(inspect_url)
            time.sleep(1)
    return stuck_urls


def main():
    """
    The main function for command line use.
    """
    description = 'Find all submissions in an A+ course that are not "ready" or "rejected".'
    argp = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=description)
    argp.add_argument('--config', default='config.yaml',
                      metavar='C',
                      help='The config YAML file with access token and course id')
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
    stuck_urls = find_stuck_submissions(access_token, api_url, course_id)

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
