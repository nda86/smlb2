#!/usr/bin/env bash
dbuser=postgres
backupname=$1
cat $backupname | docker-compose exec -T db psql -U $dbuser
