# sources/distributed-fs/tahoe-lafs/src/allmydata/__main__.py

## Purpose

This module makes `python -m allmydata` behave like the Tahoe-LAFS command-line entry point.

## Important APIs, Types, And Functions

It imports `run` from `allmydata.scripts.runner` and, when executed as `__main__`, exits with `sys.exit(run())`.

## Control Flow

The module has no behavior on import beyond imports. Under module execution, it calls the shared runner and propagates the returned exit code.

## State And Persistence

No local state or persistence is owned here.

## Dependencies And Integration Points

It integrates Python module execution with the same runner used by the `tahoe` console script declared in `pyproject.toml`.

## Risks

Any import error or behavior change in `allmydata.scripts.runner.run` directly affects `python -m allmydata`. There is no wrapper error handling here.

## Test Signals

Run `python -m allmydata --help` and compare behavior and exit status with the `tahoe --help` console script.
