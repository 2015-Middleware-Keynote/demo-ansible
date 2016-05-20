#!/bin/bash

# exit on any error
set -e

# determine router scale
ROUTER_SCALE=$(oc get dc/router -o go-template='{{.spec.replicas}}')

# find number of running routers
NUM_ROUTERS=$(oc get pod -o go-template='{{range .items}}{{ .metadata.name }} {{.status.phase}}{{"\n"}}{{ end }}' | grep router | grep Running | wc -l)

[ $NUM_ROUTERS -eq $ROUTER_SCALE ]
