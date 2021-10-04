#!/usr/bin/env bash

set -o errexit          # Exit on most errors
set -o errtrace         # Make sure any error trap is inherited
set -o nounset          # Disallow expansion of unset variables
set -o pipefail         # Use last non-zero exit code in a pipeline

# variable defaults
print_help=false
verbose=false
dry_run=false
allow_superuser=false
disable_dirs=""
disable_dir_arr=
cleanup_method="rm"
do_cleanup=false
sys_crit_dir_arr="(/)"

__script_help() {
  cat << EOF
Usage: $0 [ OPTIONS ] <directory_path>

To cleanup a directory

Options:
  -h --help   		                Prints this help
  -v --verbose               		Enables verbose output
  -d --dry				Dry run of script (Doesn't execute any cleanup commands in real)
  --allow-superuser			Allows cleanup of directory with superuser account
  --disable-dirs=<dir1,dir2,...,dirn>	Disallows cleanup of directories listed as comma separated values.
                        		this option can be used to specify critical directories in the user's system.
                                        sysroot (/) is always disabled. 
  --with-find				Uses find and delete command for cleanup instead of rm
EOF
}

__script_usage() {

  >&2 __script_help
  exit 2
}

__parse_params() {

  parsed_arguments=$(getopt -n $0 -o hvdf --long help,verbose,dry,allow-superuser,disable-dirs:,with-find -- "$@")
  if [ $? -ne 0 ] ; then
    __script_usage
  fi
  eval set -- "$parsed_arguments"
  unset parsed_arguments

  while true
  do
    case "$1" in
      -h | --help)
         print_help=true
         break ;;
      -v | --verbose)
         verbose=true
         shift ;;
      -d | --dry)
         dry_run=true
         shift ;;
      --allow-superuser)
         allow_superuser=true
         shift ;;
      --disable_dirs)
         disable_dirs="$2"
         shift 2;;
      --with-find)
         cleanup_method="find"
         shift ;; 
      --)
         shift; break ;;
       *)
         __script_usage;;
    esac
  done

  if ${print_help}; then
    __script_help
    exit
  fi

  if [[ $# -ne 1 ]]; then
    >&2 echo "Expects a single argument"
    __script_usage
  else
    target_dir=$(readlink -f "$1")
  fi
}

__is_boolean() {

  local variable_name=$1
  case "${!variable_name}" in
    true|false|yes|no|y|n|1|0|enable|disable)
      break ;;
    *)
      echo "${variable_name} must be a valid boolean"
      return 1;;
  esac
}

__prepare_variables() {

  local validation_errors=0

  if [[ "${disable_dirs}" != "" ]]; then
    IFS=', ' read -r -a disable_dir_arr <<< "$disable_dirs"
    for dir in "${disable_dir_arr[@]}"; do
      __pathname_validator ${dir} || ((validation_errors+=1))
    done
  fi 

  [[ ${validation_errors} -eq 0 ]] || __script_usage;
}

__pathname_validator() {
  local string=$1
  if [[ "$string" = /* ]]; then
     return 0
  else
     >&2 echo "${string} should be an absolute path"
     return 1
  fi
}

__superuser_check() {
  : 
}

__targetdir_check() {

  for dir in "${sys_crit_dir_arr[@]}"; do
    if [[ "${target_dir}" == "$(readlink -f $dir)" ]]; then
      >&2 echo "Target dir: '${target_dir}' is a system critical directory"
      exit 2
    fi
  done

  for dir in "${disable_dir_arr[@]}"; do
    if [[ -d ${dir} ]]; then 
      if [[ "${target_dir}" == "$(readlink -f $dir)" ]]; then
        >&2 echo "Target dir: '${target_dir}' is in disabled directories list"
        exit 2
      fi 
    fi
  done 

}

__debug_echo() {
  if [[ ! -t 0 ]]; then
    cat
  fi
  printf -v cmd_str '%q ' "$@"; echo "$cmd_str" >&2
}

__rm_cleanup() {
 __verbose_echo "Emptying contents of ${target_dir}"
 __verbose_echo rm -rf -- "${target_dir}"/*
 if ! ${dry_run}; then
   rm -rf -- "${target_dir}"/* 
 fi  
 #TODO: Delete hidden files
}

__verbose_echo() {
  if ${verbose}; then
    echo "$@"
  fi
}

main() {

  __parse_params "$@"
  __prepare_variables

  ${allow_superuser} || __superuser_check  
  __targetdir_check 
  
  case "${cleanup_method}" in
    rm)
      __rm_cleanup;;
    find)    
      __find_cleanup;;
  esac
}

main "$@"
