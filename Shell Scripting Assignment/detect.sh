#!/bin/bash

# input is given as: ./detect.sh clean_log.csv whitelist.txt firewall_rules.sh

# Take input into variables for clean_log, whitelist, and output file
CLEAN_LOG=$1
WHITELIST=$2
OUTPUT_FILE=$3

#grep command to find lines with "Failed password", extracting IP by identifiying the pattern of an IP address, coutning the occurrences of each IP, and filtering those with more than 10 failed attempts
suspects=$(grep "Failed password" "$CLEAN_LOG" | 
           grep -Eo '([0-9]{1,3}\.){3}[0-9]{1,3}' | 
           sort | uniq -c | 
           awk '$1 > 10 { print $2 ":" $1 }')

# Loop through the suspects and check against the whitelist, if not whitelisted, add an iptables rule to the output file
# Clear the output file before the loop so you don't get duplicates on multiple runs
> "$OUTPUT_FILE"

# Loop through the suspects
for entry in $suspects; do
    ip=${entry%:*}
    count=${entry#*:}
    is_whitelisted=false
    # Read the whitelist line by line
    while IFS= read -r white_ip || [[ -n "$white_ip" ]]; do
        #This caused a lot of problems while testing the file given by the TA because 
        # 1. Remove carriage returns (\r)
        clean_white_ip="${white_ip//$'\r'/}"
        # 2. Remove all spaces
        clean_white_ip="${clean_white_ip// /}"
        # 3. Remove horizontal tabs
        clean_white_ip="${clean_white_ip//$'\t'/}"
        # Skipping empty lines in the whitelist
        if [[ -z "$clean_white_ip" ]]; then
            continue
        fi
        # Compare the suspect IP with the cleaned whitelist IP
        if [[ "$ip" == "$clean_white_ip" ]]; then
            is_whitelisted=true
            break
        fi
    done < "$WHITELIST"
    # If the IP is NOT whitelisted, add it to the fresh output file
    if [[ "$is_whitelisted" == false ]]; then
        echo "iptables -A INPUT -s $ip -j DROP # Blocked after $count failed attempts" >> "$OUTPUT_FILE"
    fi
done



