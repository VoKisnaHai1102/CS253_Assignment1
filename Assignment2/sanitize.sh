#!/bin/bash

#input is given as: ./sanitize.sh auth.log
#Take input into log_file variable
LOG_FILE=$1

#Multiple sed commands to clean the log file and output to clean_log.csv using the rules given in the problem statement
sed -e '/\[CORRUPT-DATA\]/d' \
    -e 's/user=root/user=SYS_ADMIN/g' \
    -e 's/user=admin/user=SYS_ADMIN/g' \
    -e 'y/|/,/' "$LOG_FILE" > clean_log.csv

