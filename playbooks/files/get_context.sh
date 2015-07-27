#!/bin/bash

set -eu
oc config view --flatten -o template -t '{{with index .contexts 0}}{{.name}}{{end}}'
