#!/bin/bash

#input is given as: ./timeline.sh clean_log.csv
LOG_FILE=$1

awk -F',' '/Failed password/ {
    #  Split the datetime into an array
    split($1, datetime, " ")
    split(datetime[2], hrs, ":")

    if (hrs[1] != "") {
        hour = sprintf("%02d", hrs[1] + 0)
        count[hour]++
    }
}
END {
    for (h = 0; h <= 23; h++) {
        hour_key = sprintf("%02d", h)
        
        # Only printing if the count is strictly greater than zero
        if (count[hour_key] > 0) {
            printf "Hour %s: %d failed attempts\n", hour_key, count[hour_key]
        }
    }
}' "$LOG_FILE"

#After processing all lines, printing the count in a particular format given in the question.


