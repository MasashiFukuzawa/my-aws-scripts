#============================================================================================#
# This script interactively selects a log group in AWS CloudWatch and then streams its logs, #
# defaulting to the last 24 hours if no time range is provided as an argument.               #
# Usage: sh ./tail-cloudwatch-logs.sh 10m                                                    #
#============================================================================================#

#!/bin/bash

set -e

LOG_GROUP=`aws logs describe-log-groups | jq '.logGroups[] | .logGroupName' -r | peco`

if [ "$1" != "" ]; then
	SINCE=$1
else
	SINCE=24h
fi

aws logs tail --follow $LOG_GROUP --since=$SINCE
