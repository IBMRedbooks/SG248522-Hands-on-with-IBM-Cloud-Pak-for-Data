#!/bin/bash

RIGHT_NOW=$(date +"%x %r %Z")
TIME_STAMP="Updated on $RIGHT_NOW by $USER"
PAYLOAD="payload"
DB2_DOCKER_NAME="db-test"
DB2_DATA_DIR="/data/db2"    #note this must exist on the system hosting podman
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

__loadDB2Docker()
{
   $D images > /dev/null 2>&1; rc=$?;
   if [[ $rc != 0 ]]; then
        echo "Docker Not Installed. Are you on ICP4D cluster environment ?"
        exit 1
   fi

  #run setup the payload
 
  echo -e "\nLoading Docker $DB2_DOCKER_NAME ..."
  $D run -d --name $DB2_DOCKER_NAME -p 50000:50000 --env-file ./db_env -v ${DB2_DATA_DIR}:/database:z --privileged=true  ibmcom/db2
  #Wait couple of minutes to make sure db2 instance started and online
  echo -e "\nWaiting 3 minutes until Db2 instance has started..."
  
  sleep 180
 
   echo -e "\nMaking some space for data in the db2 container"
   #make a sample directory
   $D   exec $DB2_DOCKER_NAME bash -c  "mkdir -p /samples/payload"

   echo -e "\nCreate a directory to hold the scripts"
   $D   exec $DB2_DOCKER_NAME bash -c  "mkdir -p /samples/scripts"

   echo -e "\nMoving Payload to DB2"
   #push the payload
   $D cp data  $DB2_DOCKER_NAME:/samples/payload
   $D cp load.sh  $DB2_DOCKER_NAME:/samples/payload
   $D cp run_bank.sh  $DB2_DOCKER_NAME:/samples/payload

   echo -e "\nDB2 being loaded with data for you to try out"
   #run setup the payload

   $D exec  $DB2_DOCKER_NAME  bash -c "cd /samples/payload && chmod -R 777 /samples  &&  ./load.sh"
}
__loadDB2Docker