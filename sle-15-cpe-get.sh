#!/usr/bin/env bash

osc -A https://api.suse.de/ api -X GET "/source/SUSE?view=productlist&expand=1"
