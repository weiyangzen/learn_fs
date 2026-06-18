# sources/user-network-fs/impacket/.github/workflows/build_and_test.yml

## Purpose

`build_and_test.yml` defines Impacket's main GitHub Actions CI workflow. It performs syntax linting, runs the tox-based non-remote unit test suite across supported Python versions, builds a wheel, and attempts to build the Docker image.

## Important APIs, Types, and Functions

The workflow is named `Build and test Impacket` and triggers on `push` and `pull_request`. It defines `DOCKER_TAG: impacket:latests`. Jobs are `lint`, `test`, and `docker`. `lint` uses `actions/checkout@v3`, `actions/setup-python@v4`, installs `flake8`, and runs strict syntax checks plus non-blocking style warnings. `test` runs a matrix over Python 3.9 through 3.13 and experimental `3.14-dev`, installs tox dependencies, runs `tox -- -m 'not remote'`, and builds a wheel. `docker` builds the repository Dockerfile and is allowed to fail.

## Control Flow

All jobs are skipped for same-repository pull requests because their `if` condition allows pushes or pull requests whose head repo differs from the base repository. `test` and `docker` depend on `lint`. The test matrix disables fail-fast and marks only the 3.14-dev include row as experimental with `continue-on-error`. The Docker job also has `continue-on-error: true`.

## State and Persistence Behavior

The workflow creates ephemeral CI virtual environments, tox environments, wheel artifacts in the workspace, and Docker build layers on the runner. It does not upload artifacts in this file. Persistent external state is limited to GitHub check results.

## Dependencies and Integration Points

It integrates with `requirements.txt`, `requirements-test.txt`, `tox.ini`, `setup.py`, and `Dockerfile`. It depends on GitHub-hosted Ubuntu runners, official checkout/setup-python actions, PyPI availability, tox-gh-actions configuration, and Docker build support.

## Risks and Edge Cases

`DOCKER_TAG` contains the likely typo `latests`. The pull request `if` condition appears inverted from common security patterns because it skips same-repo PRs and runs fork PRs; if secrets were added later this would matter. Pinning actions only by major version and using Python `3.14-dev` can introduce drift. The flake8 warning step is exit-zero, so many style regressions remain advisory. Docker failures do not fail the workflow.

## Test Signals

The primary signal is a successful GitHub Actions run with lint, tox matrix, wheel build, and Docker build logs. Local approximations are `flake8` with the same flags, `tox -- -m 'not remote'`, `python setup.py bdist_wheel`, and `docker build -t impacket:latests .`.
