#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Description: Create Task in Jira

"""
from __future__ import print_function

import argparse
import getpass
from os import environ
from jira import JIRA


def getargs():
    """
    Supports the command-line arguments listed below.
    """
    parser = argparse.ArgumentParser(
        description='Just create an jira issue and close it')
    parser.add_argument('-s', '--host', required=False, default='https://jira/jira', action='store',
                        help='Jira URL')
    parser.add_argument('-u', '--user', required=False, action='store',
                        help='User name to use when connecting to host, u can use env variable JIRA_USER as well')
    parser.add_argument('-p', '--password', required=False, action='store',
                        help='Password to use when connecting to host')
    parser.add_argument('--project', required=False, default='15195', action='store',
                        help='jira project pid')
    parser.add_argument('--subject', required=True, action='store',
                        help='jira issue subject')
    parser.add_argument('--description', required=False, default='n/a', action='store',
                        help='jira issue desc')
    parser.add_argument('--close', required=False, default='160', action='store',
                        help='close issue immediatly with transition id')

    args = parser.parse_args()
    return args


def main():
    """
    Create a jira issue
    """
    args = getargs()

    if not args.user:
        try:
            if environ.get('JIRA_USER') is not None:
                username = environ.get('JIRA_USER')
            else:
                raise()
        except:
            print('No user and no environment variable (JIRA_USER) provided.')
            exit()
    else:
        username = args.user

    if not args.password:
        try:
            password = getpass.getpass()
        except Exception as error:
            print('ERROR', error)
            exit()
    else:
        password = args.password

    options = {'server': args.host}

    jira = JIRA(options, basic_auth=(username, password))

    issue_dict = {
        'project': {'id': args.project},
        'summary': args.subject,
        'description': args.description,
        'issuetype': {'name': 'Änderungsanforderung'},
    }
    # Create Issue
    issue = jira.create_issue(fields=issue_dict)
    print(args.host + '/browse/' + str(issue))

    # Label Issue
    issue.fields.labels.append(u'daily_horror')
    issue.update(fields={"labels": issue.fields.labels})

    # Close Issue
    jira.transition_issue(issue, args.close)


if __name__ == "__main__":
    main()
