#!/bin/bash
LOG_FILE=$1

echo "Target Port Analysis"
echo "--------------------"

awk -F'[ ,=]+' '/Failed password/ {
    for (i = 1; i < NF; i++) {
        # Using tolower() just in case the log capitalizes "Port"
        if (tolower($i) == "port") {
            port = $(i+1)
            #removing any non-numeric characters from the port variable to ensure we only count valid port numbers
            gsub(/[^0-9]/, "", port)
            
            # Only count if we actually have a valid port number left
            if (port != "") {
                count[port]++
            }
        }
    }
}
END {
    for (p in count) {
        printf "Port %-4s : %d attempts\n", p, count[p]
    }
}' "$LOG_FILE" | sort -k4,4nr
#sorting in descending order of attempts. It is the fourth field hence k4 and 4nr for numeric reverse sort.