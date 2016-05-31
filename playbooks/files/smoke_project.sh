#!/bin/bash

SMOKEUSER=$1

# determine if app has been created
oc get bc/smoke -n $SMOKEUSER-smoke

# create if not
if [ $? -ne 0 ]
then
  oc new-app openshift/php~https://github.com/gshipley/smoke.git -n $SMOKEUSER-smoke
fi

# determine latest build for the project
BUILDNUM=$(oc get bc/smoke -n $SMOKEUSER-smoke -o template --template '{{.status.lastVersion}}')

# check status of build
BUILDSTATUS=$(oc get build smoke-$BUILDNUM -n $SMOKEUSER-smoke -o template --template '{{ .status.phase }}')

# if failed or error, exit immediately
if [[ ($BUILDSTATUS == "Failed" || $BUILDSTATUS == "Error") ]]
then
  exit 255
fi

# if complete, exit now
if [[ $BUILDSTATUS == "Complete" ]]
then
  exit 0
fi

# if not complete, wait up to 5 minutes for build to complete
# 5 minutes = 300 seconds
# 300 seconds = 30 ten second loops

LOOP=0
while [ $LOOP -lt 30 ]
do
  BUILDSTATUS=$(oc get build smoke-$BUILDNUM -n $SMOKEUSER-smoke -o template --template '{{ .status.phase }}')
  if [[ $BUILDSTATUS == "Complete" ]]
  then
    exit 0
  fi
  LOOP=$((LOOP+1))
  sleep 10
done

exit 255
