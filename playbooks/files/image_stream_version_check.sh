#!/bin/bash

set -e

# determine the image stream version tag
oc get template $1 -n $2 -o go-template='{{range .parameters}}{{if eq .name "IMAGE_VERSION"}}{{println .value}}{{end}}{{end}}'
