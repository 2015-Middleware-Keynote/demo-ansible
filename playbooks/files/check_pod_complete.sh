#!/bin/bash

# exit on any error
set -e

oc get pod -o go-template='{{ range .items }}{{ .metadata.name }} {{ range .status.conditions }}{{ .reason }}{{ end}} {{ "\n" }}{{ end }}' | grep $1 | grep "Complete"
