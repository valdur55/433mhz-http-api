#!/usr/bin/env bash
options=$(awk -F"," '{gsub(/\"/,""); gsub(/ /, " ") ; print$1}' shortcuts.csv | tail -n +2)
chosen="$(echo -e "$options" | rofi -dmenu)"

if [[ -z $choosen ]]
  then
    send_433 $chosen
fi
