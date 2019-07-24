"""
EC2インスタンスのセキュリティグループを付与・取るプログラム

実行方法
    % python myapp.py add i-xxxxxxxxxxx sg-xxxxxxxxxx
    % python myapp.py del i-xxxxxxxxxxx sg-xxxxxxxxxx

引数
    param1: 追加(add) or 削除(del)
    param2: インスタンスID
    param3: EC2インスタンスから追加（削除）するセキュリティグループ

注意事項
    プログラム内ではアクセストークンの指定は行っていない。自分の環境にあわせて、設定しておくこと

"""
__author__ = 'Yoshinari Izawa'
__version__ = '1.0'
__date__ = '2019/06/28'

import boto3
import sys
import logging

def main():
    """
    メインの実行部
    """
    global mode,instid,sg
    
    mode = sys.argv[1]      # add or del
    instid = sys.argv[2]    # 複数指定は考慮していない
    sg = sys.argv[3]        # 複数指定は考慮していない
    currentsgs = []

    logging.basicConfig(level=logging.DEBUG)
    getCurrentSG()
    if mode == 'add':
        currentsgs.append(sg)
    elif mode == 'del':
        currentsgs.remove(sg)

    modifySG()

def getCurrentSG():
    """
    現在のセキュリティグループを取得する
    """
    client = boto3.client('ec2')
    try:
        response = client.describe_instances(
            InstanceIds=[
                instid
            ]
        )
    except:
        logging.error('セキュリティグループ情報が取得できません')
        print(response)
        exit()

    logging.debug(response)
    for s in response['Reservations'][0]['Instances'][0]['SecurityGroups']:
        currentsgs.append(s['GroupId'])

def modifySG():
    """
    EC2インスタンスのセキュリティグループを変更する
    """
    client = boto3.client('ec2')
    try:
        response = client.modify_instance_attribute(
            InstanceId=instid,
            Groups=currentsgs
        )
        logging.debug(response)
        if ( response['ResponseMetadata']['HTTPStatusCode'] == 200 ):
            logging.info('セキュリティグループを変更しました')
    except:
        logging.fatal('セキュリティグループを変更できません')
        exit()

if __name__ == '__main__':
    main()

