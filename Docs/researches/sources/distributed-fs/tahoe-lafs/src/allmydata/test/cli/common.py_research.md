# sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/common.py

## Purpose
Provides shared helpers for CLI tests. It normalizes option parsing and exposes a mixin that runs Tahoe CLI verbs against `GridTestMixin` client directories.

## Important APIs, Types, And Functions
`parse_options(basedir, command, args)` builds `runner.Options`, parses `--node-directory`, descends to the leaf `subOptions`, and returns the command-specific options. `CLITestMixin` extends `ReallyEqualMixin` with `do_cli_unicode()` and `do_cli()`. The Unicode path calls `run_cli_unicode()` with a selected client node directory; the byte/native path coerces verb and args with `six.ensure_str()` before calling `run_cli()`.

## Control Flow
Tests create a grid, then use `do_cli*()` to execute commands in-process with node arguments already supplied. `client_num` selects which test client directory to target. `parse_options()` is used by option-focused tests that need to inspect command parsing without executing a full command.

## State And Persistence
The helpers hold no state. They depend on test instances to provide `get_clientdir()` and any grid state. CLI commands invoked by the helpers may write into node directories.

## Dependencies And Integration Points
Depends on Tahoe script runner and common test utilities. Integrates directly with `GridTestMixin` clients and with CLI tests for backup, aliases, checks, and other commands.

## Risks And Test Signals
Incorrect string coercion can mask real command-line encoding bugs or create Python 3 type mismatches. Tests should verify Unicode aliases, native string command paths, non-default client numbers, option parsing to leaf subcommands, and stdout/stderr/return-code propagation from `run_cli*()`.
