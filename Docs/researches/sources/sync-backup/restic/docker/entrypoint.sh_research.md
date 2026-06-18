# sources/sync-backup/restic/docker/entrypoint.sh

## Purpose

This entrypoint script runs restic inside the container, optionally wrapping it with `ionice` and always wrapping it with `nice`. It handles BusyBox `ionice` quirks by only invoking `ionice` when a non-empty class is provided.

## Important APIs, Types, and Functions

- Shebang `#!/bin/sh -e` exits on command failures.
- `set -- /usr/bin/restic "$@"` makes restic plus user arguments the command.
- If `IONICE_CLASS` is non-empty, the command becomes `ionice -c "$IONICE_CLASS" -n "${IONICE_PRIORITY:-4}" ...`.
- Final `exec nice -n "${NICE:-0}" "$@"` replaces the shell with the adjusted command.

## Control Flow

At container start, the script constructs an argument vector. It conditionally prepends `ionice`, then executes `nice`, which in turn executes either restic directly or ionice/restic depending on configuration.

## State and Persistence Behavior

The script does not write state. It affects process scheduling priority and optional I/O scheduling for the restic process.

## Dependencies and Integration Points

It depends on BusyBox/Alpine `sh`, `nice`, optionally `ionice`, and `/usr/bin/restic`. It is the entrypoint declared by `docker/Dockerfile` and is controlled by image environment variables `IONICE_CLASS`, `IONICE_PRIORITY`, and `NICE`.

## Risks and Edge Cases

- Invalid `IONICE_CLASS`, `IONICE_PRIORITY`, or `NICE` values cause startup failure.
- `ionice` is skipped by default because class `0` with a priority is rejected by BusyBox.
- Since `exec` is used, signal handling is correctly transferred to the final process.

## Test Signals

Container smoke tests should run with default environment and with explicit `IONICE_CLASS`/`IONICE_PRIORITY` values. `ps` or process inspection can confirm the shell is replaced and signals reach restic.
