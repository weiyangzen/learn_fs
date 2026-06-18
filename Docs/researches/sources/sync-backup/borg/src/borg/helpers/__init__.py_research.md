# sources/sync-backup/borg/src/borg/helpers/__init__.py

## Purpose
Compatibility façade for Borg helper utilities that were split out of a historical monolithic `helpers.py`. It re-exports common helpers and owns process-wide warning and exit-code aggregation.

## Important APIs, Types, And Functions
Re-exports data structures, error classes, filesystem helpers, parsing/formatting helpers, process helpers, progress indicators, time helpers, yes/no utilities, and msgpack helpers. Defines `workarounds`, `warning_info`, `_warnings_list`, `_exit_code`, `add_warning`, `classify_ec`, `max_ec`, `set_ec`, `init_ec_warnings`, `get_ec`, `get_reset_ec`, and `do_show_rc`.

## Control Flow
Importing this module imports many helper submodules and constants, so it is a high-fanout dependency. Warning collection appends typed tuples. Exit code handling classifies return codes into success, warning, error, or signal; `set_ec` keeps the more severe value; `get_ec` returns explicit error/signal/warning codes first, otherwise derives a warning code from collected warnings.

## State And Persistence
State is process-global: `_warnings_list`, `_exit_code`, and `workarounds` from `BORG_WORKAROUNDS`. `init_ec_warnings` resets mutable globals and can accept an existing warning list, which makes test isolation important. Nothing is persisted to disk.

## Dependencies And Integration Points
Almost every Borg command path imports from this package. `helpers.process` also imports back from `..helpers`, creating import-order sensitivity. `do_show_rc` uses the `borg.output.show-rc` logger and must never interfere with program exit.

## Risks And Edge Cases
The compatibility import surface can hide circular dependencies and slows import. Global exit/warning state must be reset between tests and top-level invocations. `classify_ec` rejects unknown codes, so additions to constants must keep ranges coherent. Multiple warning codes collapse to generic `EXIT_WARNING`.

## Test Signals
Existing helper package tests should cover warning aggregation, modern versus legacy exit code mode, `get_reset_ec`, `do_show_rc` logging resilience, and import compatibility for names historically exported from `borg.helpers`.
