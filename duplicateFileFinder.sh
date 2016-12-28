#!/bin/bash -
#===============================================================================
#
#          FILE: dpr.sh
#
#         USAGE: ./dpr.sh
#
#   DESCRIPTION:Duplicate file remover
#		ref: http://superuser.com/questions/386199/how-to-remove-duplicated-files-in-a-directory
#
#       OPTIONS: ---
#  REQUIREMENTS: bash version > 4.*
#          BUGS: ---
#         NOTES: TODO:
#			* add console output,
#			* use timer function for benchmark
#			* check bash version
#        AUTHOR: talayhan
#  ORGANIZATION:
#       CREATED: 27-12-2016 19:03
#      REVISION:  ---
#===============================================================================

#set -o nounset                              # Treat unset variables as an error

declare -A arr
shopt -s globstar
__ScriptVersion="0.1"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

#===  FUNCTION  ================================================================
#         NAME:  usage
#  DESCRIPTION:  Display usage information.
#===============================================================================
function usage ()
{
	echo "Usage :  $0 [options] [--]

    Options:
    -h|help       Display this message
    -d|dir        Specify directory (ex: -d \$HOME)
    -v|version    Display script version

    script dir: $SCRIPT_DIR"

}    # ----------  end of function usage  ----------

function show-date() {
	date +"%T.%N"
}

function main() {
	for file in **; do
		[[ -f "$file" ]] || continue
		checkSum=`md5sum "$file" | awk '{print $1}'`
		if ((arr[$checkSum]++)); then
			echo "[+] Duplicated file found: $file"
			rm $file
		fi
	done
}

function checkDir() {
	if [[ -d $DIR ]]; then
		cd $DIR
	else
		echo Something went wrong about :$DIR
		usage
		exit
	fi
}

#-----------------------------------------------------------------------
#  Handle command line arguments
#-----------------------------------------------------------------------

while getopts ":hd:v" opt
do
  case $opt in

	h|help     )  usage; exit 0   ;;

	d|dir      )  DIR=${OPTARG}; checkDir; main; exit 0   ;;

	v|version  )  echo "$0 -- Version $__ScriptVersion"; exit 0   ;;

	* )  echo -e "\n  Option does not exist : $OPTARG\n"
		  usage; exit 1   ;;

  esac    # --- end of case ---
done
shift $(($OPTIND-1))

