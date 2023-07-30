#============================================================================================#
# A script to identify AWS Batch Jobs that have been in the RUNNING status for over X hours. #
# Usage: sh ./long-running-aws-batch-job-monitor.sh sample-job-queue ap-northeast-1 86400    #
#============================================================================================#

#!/bin/bash

set -e

jobQueueName=$1
awsRegion=$2
elapsedTimeThreshold=${3:-14400} # seconds

now=`date +%s`
longRunningJobsCount=0
longRunningJobsDe=""

echo "Total jobs: $(aws batch list-jobs --job-queue $jobQueueName --job-status RUNNING | jq '.jobSummaryList | length')"

jobList=()
while IFS= read -r line; do
	jobList+=("$line")
done < <(aws batch list-jobs --job-queue $jobQueueName --job-status RUNNING | jq -r '.jobSummaryList[] | "\(.jobId) \(.jobName)"')

for jobInfo in "${jobList[@]}"; do
	jobId=$(echo $jobInfo | cut -d ' ' -f1)
	jobName=$(echo $jobInfo | cut -d ' ' -f2)
	echo "jobId=$jobId, jobName=$jobName"

	details=()
	while IFS= read -r line; do
		details+=("$line")
	done < <(aws batch describe-jobs --jobs $jobId | jq -r '.jobs[] | "\(.startedAt) \(.container.logStreamName)"')

	startedAt=$(echo ${details[0]} | cut -d ' ' -f1)
	logStreamName=$(echo ${details[0]} | cut -d ' ' -f2)

	elapsed=$(expr $now - $(($startedAt / 1000)))
	if [ $elapsed -gt $elapsedTimeThreshold ]; then
		echo "Hit! jobId: $jobId"
		longRunningJobsCount=$((longRunningJobsCount+1))
		longRunningJobs+="■ AWS Batch URL\nhttps://$awsRegion.console.aws.amazon.com/batch/home?region=$awsRegion#jobs/detail/$jobId\n\n"
		longRunningJobs+="■ CloudWatch Logs URL\nhttps://$awsRegion.console.aws.amazon.com/cloudwatch/home?region=$awsRegion#logEventViewer:group=/aws/batch/job;stream=$logStreamName\n\n"
		longRunningJobs+="-----------------------------\n\n"
	fi
done

echo longRunningJobsCount=$longRunningJobsCount
echo $longRunningJobs
