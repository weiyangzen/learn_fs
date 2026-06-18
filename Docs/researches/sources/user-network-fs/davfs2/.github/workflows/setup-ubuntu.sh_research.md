# sources/user-network-fs/davfs2/.github/workflows/setup-ubuntu.sh

## Purpose
This shell script installs the Ubuntu packages needed by davfs2's CI workflow.

## Important APIs and commands
It runs with `/bin/sh`, enables `set -ex`, defines `PACKAGES` as `libneon27-dev`, `meson`, `ninja-build`, and `po4a`, then invokes `sudo -E apt-get -y install $PACKAGES`.

## Control flow
The script is a single install step. `set -e` stops on errors and `set -x` logs commands for CI diagnosis.

## State and persistence behavior
It mutates only the ephemeral CI runner by installing apt packages. No repository files are changed.

## Dependencies and integration points
It assumes an Ubuntu GitHub runner with apt metadata already suitable for package install. It supports `.github/workflows/makefile.yml`.

## Risks
No `apt-get update` is run, so stale runner package indexes can break installs. Package names are Ubuntu-specific. `sudo -E` preserves environment variables, which is normal in CI but should be intentional.

## Test signals
The workflow build is the main signal. A shellcheck pass and periodic CI run on a fresh runner image can catch package rename or apt metadata issues.
