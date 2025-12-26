#!/usr/bin/env bash

command=$(echo "$@" | sed "s/ /_/g" | sed "s/-/_/g")
host="nuti"
altHost="printer"


wget -4 "http://$host.local:5433/?cmd=$command" -O - || wget "http://$altHost.local:5433/?cmd=$command" -O - -4

