#!/bin/bash
set -e
#src=~/.bin/fuzzy

################
# run fuzzy finder within set location
################

source ~/.zshenv #necessary cause env isn't sourced when executed by i3wm

main() {
	file_to_edit=$(cd $(cat $NAV/.location) && export SKIM_DEFAULT_COMMAND="find . -not -regex '.*\.\(toc\|gz\|aux\|fdb_latexmk\|out\|log\|xopp~\)' -not -path '*__pycache__/*' -not -path '*/.*' -not -path '*.ipynb_checkpoints/*'" && sk -m) # --query="$given_file" # --preview "~/.bin/preview.sh {}" 

  loc=$(cat $NAV/.location)
  open "$loc/$file_to_edit"
  # echo "before test"
  # echo $(open $loc/$file_to_edit | grep "No application knows")
  # if [ -n $(open $loc/$file_to_edit | grep -E ".*\.(py|txt|png)") ] ; then
  #     echo "application found"
  # fi
}

main
