#!/bin/bash

RIGHT_NOW=$(date +"%x %r %Z")
TIME_STAMP="Updated on $RIGHT_NOW by $USER"
PAYLOAD="payload"
DB2_DOCKER_NAME="redbook-test"
# D=docker
# Check if podman or docker command was found
if command -v podman &> /dev/null;then
  D="podman"
elif command -v docker &> /dev/null;then
  D="docker"
else
  echo "podman or docker command was not found."
  exit 99
fi


##### Functions

__configureDBLineageSettings()
{

   if [[ ! '$D ps | grep $DB2_DOCKERNAME' ]]; then
     echo -e "\nRedbbok test container not running"
     exit
   fi

   echo -e "\nCopy lineage scripts to container"
   #push the payload
   $D cp db-lineage-settings.sh  $DB2_DOCKER_NAME:/samples/scripts
   $D cp lineage-settings.sql  $DB2_DOCKER_NAME:/samples/scripts

   echo -e "\nRunning lineage configuration script"
   $D exec  $DB2_DOCKER_NAME  bash -c "cd /samples/scripts && chmod -R 777 db-lineage-settings.sh  &&  ./db-lineage-settings.sh"

}
__configureDBLineageSettings