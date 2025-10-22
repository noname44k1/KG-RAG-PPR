#!/bin/bash

# Khởi tạo biến
WORKING_DIR="./health_care"
WORKING="health_care"
sindex=1
eindex=300
USAGE_FILE="${WORKING}/usage/usage_${sindex}_${eindex}.json"
LOG_PROCESS_FILE="${WORKING}/query_process.txt"
RESULT_FILE="${WORKING}/eval/result.json"
samples_dir="../data/ground_truth_300_clean.json"
corpus_dir="../data/health_care.txt"

python query.py --working_dir $WORKING_DIR --sindex $sindex --eindex $eindex --usage $USAGE_FILE --log $LOG_PROCESS_FILE --result_file $RESULT_FILE --samples_dir $samples_dir --corpus_dir $corpus_dir

# while [ $eindex -le 1000 ]
# do
#     echo "Running: sindex=$sindex, eindex=$eindex"
#     USAGE_FILE="usage_${sindex}_${eindex}.json"
#     python3 index.py --sindex $sindex --eindex $eindex --gemini $GEMINI --usage $USAGE_FILE --log $LOG_PROCESS_FILE

#     sindex=$eindex
#     eindex=$((eindex + 100))
# done

docker run --rm -v health_care:/volume -v $(pwd):/backup busybox tar czf /backup/volume_backup.tar.gz -C /volume .