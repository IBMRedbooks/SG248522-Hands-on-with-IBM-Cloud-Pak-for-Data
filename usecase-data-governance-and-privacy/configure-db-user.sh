#!/bin/bash

RIGHT_NOW=$(date +"%x %r %Z")
TIME_STAMP="Updated on $RIGHT_NOW by $USER"
PAYLOAD="payload"
DB2_DOCKER_NAME="db-test"
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

__configureDB2ForLineage()
{

   if [[ ! '$D ps | grep $DB2_DOCKERNAME' ]]; then
     echo -e "\nDb2 container not running"
     exit
   fi

   echo -e "\nCopy create-test-user script to container"
   #push the payload
   $D cp create-test-user.sh  $DB2_DOCKER_NAME:/samples/scripts

   echo -e "\nRunning create test user script"
   $D exec  $DB2_DOCKER_NAME  bash -c "cd /samples/scripts && chmod -R 777 create-test-user.sh  &&  ./create-test-user.sh"

}
__configureDB2ForLineage