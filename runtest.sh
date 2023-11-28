#!/bin/bash

set -x

./sync_client --server "$SERVER" --set "$STATE" --job "${RSTRNT_JOBID:-1}"
for host in $HOSTS
do
	./sync_client --server "$SERVER" --job "${RSTRNT_JOBID:-1}" --wait "$host" "$STATE"
done
