#!/usr/bin/env bash

set -x
set -eu

# pytest --cov

black .
flake8
