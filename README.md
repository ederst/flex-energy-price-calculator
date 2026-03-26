# Flexible Energy Price Calculator

This is a very **quick and dirty** little app which can calulate flex energy prices of electricity suppliers based on their tariff models.

I made this to pre preview the price for the upcoming month so that I do not have to do it manually myself all the time.

Possible TODOs:

* Improve the code ;)
* Make it so that it builds a static website
* Make the static website available via GH pages
* Create GH Actions with cron jobs for updating GH pages (aka CI/CD)
* ???
* Profit (no not really, just some personal gains I guess)

## Getting Started

Install `poetry` and/or `direnv` and clone this repository.

```shell
git clone <repourl>
poetry install
```

Create `.envrc-secrets` and find out which headers you have to set for yourselves.

```shell
# Calculate for single month
poetry run flep --start 2024-03 --model oekoflow1.0
poetry run flep -s 2024-03 -m oekoflow1.0

# Calculate for date range
poetry run flep --start 2024-01 --end 2024-03 --model gogreenenergyflex
poetry run flep -s 2024-01 -e 2024-03 -m gogreenenergyflex

# List available models
poetry run flep --list
poetry run flep -l

# Show help
poetry run flep --help
```

Currently the following models are supported:

* oekoflow1.0
* gogreenenergyflex
* gogreenenergyflexfuture
* fullmonth
