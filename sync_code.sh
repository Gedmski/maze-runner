#!/bin/bash

# Create directory on remote machines
for host in $(cat machines.txt); do
    if [ "$host" != "localhost" ]; then
        ssh $host "mkdir -p ~/maze-runner"
    fi
done

# Sync code to remote machines
for host in $(cat machines.txt); do
    if [ "$host" != "localhost" ]; then
        rsync -avz --exclude '__pycache__' --exclude '*.pyc' ./ $host:~/maze-runner/
    fi
done 