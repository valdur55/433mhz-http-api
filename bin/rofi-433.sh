#!/usr/bin/env bash
echo $PWD
options=$(awk -F"," '{gsub(/\"/,""); gsub(/ /, " ") ; print$1}' ~/arendus/valdur-433/shortcuts.csv | tail -n +2)
chosen="$(echo -e "$options" | rofi -dmenu)"

if [[ -z $choosen ]]
  then
    send_433 $chosen
fi
