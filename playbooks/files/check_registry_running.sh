#!/bin/bash

set -e

# check that registry deployment is nonzero
DEPLOYMENT_VERSION=$(oc get dc/docker-registry -o go-template='{{.status.latestVersion}}')

if [ $DEPLOYMENT_VERSION -ne "0" ]
then
  # find docker registry pod
  POD_NAME=$(oc get pod -o go-template='{{ range .items }}{{ .metadata.name }}{{"\n"}}{{ end }}' | grep docker-registry-$DEPLOYMENT_VERSION)

  # check if running
  STATUS=$(oc get pod $POD_NAME -o go-template='{{ .status.phase }}')

  [ $STATUS == "Running" ]
fi
