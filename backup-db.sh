#!/usr/bin/env bash
dbname=smlb
dbuser=postgres
backupname="./backup/$dbname-$(date  +%d-%m-%y_%M-%H).sql"
docker-compose exec db pg_dumpall -c -U "${dbuser}" > "${backupname}"
