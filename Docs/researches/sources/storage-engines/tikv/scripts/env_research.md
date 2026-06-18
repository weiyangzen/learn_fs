# sources/storage-engines/tikv/scripts/env

## Purpose
Runs an arbitrary command inside the TiKV Makefile environment. It is a convenience wrapper for commands that need the same setup as `make run`.

## Important Commands and Control Flow
The script enables `set -euo pipefail` and executes `make -f "$(dirname "$0")/../Makefile" run` with `COMMAND="$*"`. `exec` replaces the shell with make, so make's exit status becomes the wrapper's exit status.

## State, Dependencies, Integration
The wrapper itself writes no state; side effects belong to the command executed by the Makefile target. It depends on bash, make, the repository Makefile, and the `run` target's `COMMAND` handling.

## Risks and Test Signals
Joining arguments with `$*` can lose original argument boundaries and quoting. The path calculation assumes the script remains under `scripts/`. Running a simple command such as `./scripts/env env` should show the Makefile environment and preserve exit status.
