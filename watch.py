import sys
import argparse
import time
import json

import boto.codedeploy


def watch(codedeploy_connection, deployment_id, interval, timeout):
    start_time = time.time()
    while True:
        elapsed = time.time() - start_time
        if elapsed > timeout:
            print 'Timeout exceeded'
            sys.exit(-1)

        result = codedeploy_connection.get_deployment(deployment_id)
        info = result.get('deploymentInfo')
        status = info.get('status')
        print info.get('deploymentOverview') or status
        if status == 'Succeeded':
            sys.exit(0)
        elif status == 'Failed' or status == 'Stopped':
            sys.exit(-1)
        else:
            time.sleep(interval)

def read_deployment_id():
    return json.load(sys.stdin).get('deploymentId')

def make_argument_parser():
    parser = argparse.ArgumentParser(description='Watch aws CodeDeploy deployment status')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--interval', type=int, default=5, help='Poll interval, in seconds')
    parser.add_argument('--timeout', type=int, default=600, help='Maximum time to wait before returning an error')
    parser.add_argument('--deployment-id', help='AWS CodeDeploy deployment id; if left empty it is read from stdin as json')

    return parser

def main():
    args = make_argument_parser().parse_args()
    codedeploy_connection = boto.codedeploy.connect_to_region(args.region)
    watch(codedeploy_connection, args.deployment_id or read_deployment_id(), args.interval, args.timeout)

if __name__ == '__main__':
    main()
