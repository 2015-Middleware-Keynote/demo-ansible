#!/bin/bash

set -eu
osc config view --flatten -o template -t '{{with index .users 0}}{{.user.token}}{{end}}'
