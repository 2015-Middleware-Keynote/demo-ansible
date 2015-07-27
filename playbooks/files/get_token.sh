#!/bin/bash

set -eu
oc config view --flatten -o template -t '{{with index .users 0}}{{.user.token}}{{end}}'
