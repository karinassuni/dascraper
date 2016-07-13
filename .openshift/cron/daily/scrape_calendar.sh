#!/bin/bash

# Python modules should be run from the project root directory
cd $OPENSHIFT_REPO_DIR

python -m dascraper.eventcalendar.calendar
