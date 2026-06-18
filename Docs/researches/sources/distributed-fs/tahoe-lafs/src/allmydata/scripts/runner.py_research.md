# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/runner.py

## Purpose
Provides the top-level `tahoe` command parser and dispatcher. It combines create, admin, run, debug, file API, and invite subcommands, initializes optional Eliot logging, and runs under Twisted `task.react`.

## APIs, Types, And Control Flow
`Options` is the root Twisted `usage.Options` class with global flags (`--quiet`, `--version`, `--version-and-path`), global parameters (`--node-directory`, wormhole settings), and all subcommands. `parse_or_exit` parses argv, prints the most specific subcommand usage on errors, and exits with rc 1. `dispatch` selects the implementation module; blocking filesystem/web CLI commands are wrapped in `threads.deferToThread`, while create/run/invite/debug/admin commands are run through Deferred-aware dispatch. `run` initializes Windows fixups and calls `_run_with_reactor`; `_setup_coverage` supports multiprocess coverage when `--coverage` is present.

## State, Persistence, And Integration
No Tahoe data files are written directly. It mutates process state: stdio handles on options, `sys.argv` indirectly through invoked tools, `COVERAGE_PROCESS_START`, Twisted reactor lifecycle, and optional Eliot logging service. It integrates all command modules, magic-wormhole, Twisted threads/deferreds, and Tahoe version reporting.

## Risks And Test Signals
Risks include `SystemExit`-driven control flow, thread wrapping assumptions for blocking commands, argv conversion side effects, coverage typo in one error message, and keeping usage errors precise when nested parsers partially initialize. Test signals are `allmydata/test/test_runner.py`, CLI parser tests, run command tests, and integration tests that launch `tahoe`.
