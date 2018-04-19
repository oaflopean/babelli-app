#bin/bash
lsof -P | grep ':8080' | awk '{print $2}' | xargs kill -9

