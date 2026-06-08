## reusable workflows

This repository contains reusable GitHub Actions workflows for C3S projects. There is currently one CI workflow for Jupyter Notebook QA automation.


### notebook-qa

This workflow implements QA automation for Jupyter Notebooks. The checks below run automatically — all checks that are not skipped or disabled must pass for the workflow to succeed.

#### Checks

**Code linting** (`linter`) — Runs `ruff check` on all code cells. No Python lint violations allowed.

**Code formatting** (`formatter`) — Runs `ruff format --check` on code cells. Code cells must conform to `ruff` formatting rules.

**Notebook linting** (`pynblint`) — Runs `pynblint` on each notebook. Checks notebook-level quality issues such as non-linear execution order, empty cells, or untitled notebooks.

**Link availability** (`links`) — Runs `lychee` against all notebooks. Every URL in markdown and code cells must be reachable.

**Notebook execution** (`execute`) — Executes each notebook end-to-end with `ploomber-engine`. The notebook must run without errors. Memory usage and runtime are profiled per cell, checked against performance-test thresholds, summarized in GitHub Actions, and uploaded as artifacts.

**Version metadata** (`metadata`) — Looks for `**Last updated:** YYYY-MM-DD` (e.g. `**Last updated:** 2025-01-15`) in the first markdown cell(s) before any code cell. Falls back to a `README.md` in the same directory if not found in the notebook.

**Accessibility** (`accessibility`) — Runs WCAG compliance checks on notebooks using `jupyterlab-a11y-checker`.

**Figure attribution** (`figures`) — Every figure output (PNG/JPEG) in code cells must have source attribution in a nearby markdown cell (within 2 cells). Recognized attribution patterns include `source:`, `credit:`, `data from:`, `attribution:`, `reference:`, `dataset:`, a DOI, or a URL.

**License file** (`license`) — A non-empty `LICENSE` file must exist in the repository root.

**Changelog file** (`changelog`) — A non-empty `CHANGELOG.md` file must exist in the repository root.

#### How to use `notebook-qa.yml` workflow

Configure the target repository which you want to run the QA check against using this format:

```
.github/workflows/qa.yml

------------------------

name: Notebook QA

on:
  push:
    branches:
      - develop
  pull_request:
    branches:
      - develop
  workflow_dispatch:
    inputs:
      notebooks:
        description: "Space-separated list of notebook paths to check (default: all *.ipynb)"
        required: false
        type: string
        default: ""
      qa_tools_ref:
        description: "QA tools branch, tag, or commit SHA (default: reusable-workflows default branch)"
        required: false
        type: string
        default: ""

permissions:
  contents: read
  pull-requests: write

jobs:
  notebook-qa:
    uses: ecmwf-training/reusable-workflows/.github/workflows/notebook-qa.yml@main
    with:
      notebooks: ${{ inputs.notebooks || '' }}
      qa_tools_ref: ${{ inputs.qa_tools_ref || '' }}
      pr_comment_summary: true
    secrets: inherit
```

This sets up automated checks on new pull requests and merges/pushes into `develop` branch. It also allows manual Action runs in the GitHub Actions UI. Use `qa_tools_ref` when testing changes to the QA tooling from a feature branch.

The workflow writes the automated review table to the GitHub Actions job summary and, by default, updates a single managed comment on pull requests. Set `pr_comment_summary: false` to disable PR comments. The caller workflow must grant `pull-requests: write` for PR comments to work; reusable workflows cannot elevate the caller's `GITHUB_TOKEN` permissions. Pull requests from forks may still receive read-only tokens depending on the target repository settings.


#### Configuration

You can customize check behavior by adding a `.github/notebook-qa.yml` config file in the consuming repository:

```yaml
# Globally disable specific checks
disabled_checks:
  - linter
  - formatter

# Notebooks to skip entirely (all checks), supports glob patterns
skip_notebooks:
  - "./draft.ipynb" # To skip notebooks at the top level include "./" to ensure that the path is resolved
  - "notebooks/draft.ipynb"
  - "notebooks/experimental/**"

# Per-notebook check configuration
notebooks:
  "notebooks/example.ipynb":
    skip:
      - figures

# Performance-test thresholds used during notebook execution.
# Defaults are strict for learner-suitable notebooks. Set any value to null to disable it.
performance_tests:
  max_cell_memory_mb_warning: 512
  max_cell_memory_mb_fail: 1024
  max_cell_runtime_seconds_warning: 60
  max_cell_runtime_seconds_fail: 180

# Pynblint rule configuration
pynblint:
  exclude:                    # Additional rules to suppress (extends baseline)
    - untitled-notebook
  exclude_mode: extend        # "extend" (default) or "override"
```

The baseline pynblint exclusion list suppresses `missing-h1-MD-heading` (MyST notebooks use YAML frontmatter for titles). In `extend` mode (default), your `exclude` list is merged with the baseline. In `override` mode, your list fully replaces the baseline.

Available pynblint rule slugs: `non-linear-execution`, `notebook-too-long`, `untitled-notebook`, `non-portable-chars-in-nb-name`, `notebook-name-too-long`, `imports-beyond-first-cell`, `missing-h1-MD-heading`, `missing-opening-MD-text`, `missing-closing-MD-text`, `too-few-MD-cells`, `duplicate-notebook-not-renamed`, `invalid-python-syntax`, `non-executed-notebook`, `non-executed-cells`, `empty-cells`, `long-multiline-python-comment`, `cell-too-long`

Valid check IDs: `linter`, `formatter`, `pynblint`, `links`, `figures`, `metadata`, `accessibility`, `license`, `changelog`, `execute`


#### QA criteria reference

| ID    | Description               | Tool / Check           |
|-------|---------------------------|------------------------|
| 1.2.3 | Link availability         | lychee                 |
| 1.2.4 | License file              | LICENSE existence       |
| 1.2.6 | Version metadata          | metadata_checker.py    |
| 2.2.1 | Code execution            | ploomber-engine        |
| 2.2.3 | Code style                | ruff, pynblint         |
| 2.2.4 | Execution profiling       | ploomber-engine        |
| 2.2.6 | Memory profiling          | ploomber-engine        |
| 2.3.1 | Performance tests available | ploomber-engine profiling |
| 2.3.2 | Performance tests coverage | resource threshold checks |
| 3.1.3 | Accessibility             | jupyterlab-a11y-checker|
| 3.3.2 | Figure attribution        | figure_checker.py      |
| 4.2.3 | Changelog                 | CHANGELOG.md existence |


### How to configure access to cdsapi for notebook execution check

The action responsible for notebook execution allows setting a `cdsapi` key via `CDSAPI_KEY` secret set either on repository or organisation level.


### How to setup reusable-workflows repository in GitHub organisation

1. Fork this repository into your organisation
2. Leave the fork network in the newly forked repository settings
