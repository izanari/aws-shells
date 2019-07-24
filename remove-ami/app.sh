#!/bin/bash

# タグ付けされたAMIの解除およびスナップショットを削除するシェル
# 実行する前には以下を書き換えること
# CLIOPT : profileの指定が必要な場合
# FILTER : タグのkeyとvalue
# 16行目の[1:]の値。1:は直近の1世代目のみ保存して、それ以降は削除します。

set -ex

# profileは書き換えが必要であれば修正すること
CLIOPT='--profile hogehoge --output text'
FILTER='--filters Name=tag-key,Values=Type Name=tag-value,Values=test'


# AMI IDを取得する
RET=`aws ec2 describe-images --owners self --query 'reverse(sort_by(Images,&CreationDate))[1:].{id:ImageId}' $FILTER $CLIOPT` 

if [ $? != 0 ]; then
	echo "[FATAL] AWS command execution failer."
	exit 1
fi

# AMI IDを配列に格納する
AMIIDS=($RET)
if [ ${#AMIIDS[@]} == 0 ];then
	echo "[INFO] Target AMI does not exist."
	exit 0
fi

for id in "${AMIIDS[@]}"
do
	# AMIで使っているsnapshotを取得しておく
	RET=`aws ec2 describe-images --image-ids=$id --query Images[].BlockDeviceMappings[].Ebs.SnapshotId $CLIOPT`
	SNAPIDS=($RET)
	aws ec2 deregister-image --image-id $id $CLIOPT
	echo "deregister $id"
	if [ $? == 0 ]; then
		for snapid in "${SNAPIDS[@]}"
		do
			aws ec2 delete-snapshot --snapshot-id $snapid $CLIOPT 
			echo "delete snapshot $snapid"
			if [ $? == 0 ];then
				echo "[INFO] Delete snapshot($snapid)" 
			fi
		done	
	else
		echo "[ERROR] Failed to release AMI."				
	fi
done
