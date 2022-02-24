#!/usr/bin/env bash

command=$(echo "$@" | sed "s/ /_/g" | sed "s/-/_/g" | uni2ascii -aJ)
curl "http://192.168.0.15:5433/?cmd=$command"
