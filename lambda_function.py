#!/usr/bin/env python
# -*- coding: utf-8 -*-

# from __future__ import print_function

import boto3
import json
import time

event = {
    "Records": [{
        "EventVersion":
        "1.0",
        "EventSubscriptionArn":
        "arn:aws:sns:ap-southeast-1:332947256684:autoscaling:9d15fab9-cf0c-400c-9040-69cf5589e32f",
        "EventSource":
        "aws:sns",
        "Sns": {
            "SignatureVersion":
            "1",
            "Timestamp":
            "2017-06-15T06:46:52.934Z",
            "Signature":
            "HTe5GrKl9rAwLzzr+Dw4jPfUKGEnZTgOP1mlOX63/2tYvO1rAnPDeU+wlXQdcCgYdQdVgH6BRt8cZVh201/v4oW6CTTLKII6pyzjT0C1/NsHw3/zBh/d5+GH8/nNgZIrumzHEvcIBYDJeYqPXmqlSgo8SSvrV69hDfIgOeAif1efWYdLtvAi3cK5tyWH4MKkCSNuDuPJDJ2o5qjoqTKvhrlwmvth74mFbeUpQPMIqg6+NaEb3DAAoW/B+5ZaPI8ApzI0+lTWDv6/AN6DkmxWk6EFnQnUhm/IYB4/jP4bcLilUqAZkxrQ6lfb/GE6f7rJ56N5uSCZcc/1JCex7HR9tg==",
            "SigningCertUrl":
            "https://sns.ap-southeast-1.amazonaws.com/SimpleNotificationService-b95095beb82e8f6a046b3aafc7f4149a.pem",
            "MessageId":
            "b84093fd-0aa5-5cd5-8b52-c2412539efa5",
            "Message":
            "{\"AlarmName\":\"awselb-ELB-TCP-nginx-openresty-preview-High-Healthy-Hosts\",\"AlarmDescription\":\"Created from EC2 Console\",\"AWSAccountId\":\"332947256684\",\"NewStateValue\":\"ALARM\",\"NewStateReason\":\"Threshold Crossed: 1 datapoint (1.0) was greater than the threshold (0.0).\",\"StateChangeTime\":\"2017-06-15T06:46:52.892+0000\",\"Region\":\"Asia Pacific - Singapore\",\"OldStateValue\":\"OK\",\"Trigger\":{\"MetricName\":\"HealthyHostCount\",\"Namespace\":\"AWS/ELB\",\"StatisticType\":\"Statistic\",\"Statistic\":\"MINIMUM\",\"Unit\":null,\"Dimensions\":[{\"name\":\"LoadBalancerName\",\"value\":\"ELB-shop-preview\"}],\"Period\":60,\"EvaluationPeriods\":1,\"ComparisonOperator\":\"GreaterThanThreshold\",\"Threshold\":0.0,\"TreatMissingData\":\"\",\"EvaluateLowSampleCountPercentile\":\"\"}}",
            "MessageAttributes": {},
            "Type":
            "Notification",
            "UnsubscribeUrl":
            "https://sns.ap-southeast-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:ap-southeast-1:332947256684:autoscaling:9d15fab9-cf0c-400c-9040-69cf5589e32f",
            "TopicArn":
            "arn:aws:sns:ap-southeast-1:332947256684:autoscaling",
            "Subject":
            "ALARM: \"awselb-ELB-TCP-nginx-openresty-preview-High-Healthy-Hosts\" in Asia Pacific - Singapore"
        }
    }]
}

# logger = logging.getLogger()
# logger.setLevel(logging.INFO)


def execute_autoscaling_policy(cluster_name):
    print('starting exec auto scaling ' + cluster_name + ' policy')
    # all_id_list = get_ec2_instances_id(cluster_name)
    # containers_num = int(len(all_id_list))*int(num)
    # client = boto3.client('autoscaling')
    # response = client.execute_policy()
    # update_ecs_service(cluster_name, containers_num)


def update_ecs_service(cluster_name, containers_num):
    print('starting update ' + cluster_name + ' containers number to ' +
          containers_num)
    # time.sleep( 60 )
    # logger.info ("Start to update in "+ cluster_name +" container number")
    # ecs = boto3.client("ecs",region_name = 'ap-southeast-1')
    # response = ecs.update_service(cluster=cluster_name,service=cluster_name,desiredCount=int(containers_num))


def get_ec2_instances_id(cluster_name):
    instance_arn_list = []
    instance_id_list = []

    ecs = boto3.client("ecs", region_name='ap-southeast-1')
    response = ecs.list_container_instances(cluster=cluster_name)

    for arn in response['containerInstanceArns']:
        instances_arn = arn.split('/')
        instance_arn_list.append(instances_arn[1])

    response = ecs.describe_container_instances(
        cluster=cluster_name, containerInstances=instance_arn_list)

    for ec2_id in response['containerInstances']:
        instance_id_list.append(ec2_id['ec2InstanceId'])

    return instance_id_list


def wakeup_instances(cluster_name, num):

    all_id_list = get_ec2_instances_id(cluster_name)
    containers_num = int(len(all_id_list)) * int(num)

    # logger.info ("Ready to wakeup stop instance in "+ cluster_name +" environment")

    ec2 = boto3.client("ec2", region_name='ap-southeast-1')
    response = ec2.describe_instance_status(InstanceIds=all_id_list)

    if len(response['InstanceStatuses']) == len(all_id_list):
        execute_autoscaling_policy(cluster_name)
    else:
        running_ids = []
        for ids in response['InstanceStatuses']:
            running_ids.append(ids['InstanceId'])

    stopping_ids = list(set(all_id_list).difference(set(running_ids)))
    print('Instance Not Run list: ' + str(stopping_ids))
    # ec2.start_instances(InstanceIds=stopping_ids)
    # update_ecs_service(cluster_name, containers_num)


# def lambda_handler(event, context):
if __name__ == '__main__':

    raw_message = json.loads(event['Records'][0]['Sns']['Message'])
    elb_name = raw_message['Trigger']['Dimensions'][0]['value']

    raw_cluster_name = elb_name.split('-')

    print raw_cluster_name

    num = 4
    cluster_name = "-".join(raw_cluster_name[1:4]).split('/')[0]

    if raw_cluster_name[0] == 'openresty':
        num = 1
        cluster_name = "-".join(raw_cluster_name[0:3]).split('/')[0]    
    
    if raw_cluster_name[1] == 'openresty':
        num = 1
    
    
    print cluster_name
    print num

    # wakeup_instances(cluster_name, num)
