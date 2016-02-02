#!/bin/bash

set -eu
oc config view --flatten -o template --template '{{with index .users 0}}{{.user.token}}{{end}}'
