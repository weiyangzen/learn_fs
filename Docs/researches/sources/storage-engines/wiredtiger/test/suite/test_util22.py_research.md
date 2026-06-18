# sources/storage-engines/wiredtiger/test/suite/test_util22.py

## Purpose

`test_util22.py` checks help and option parsing for the `wt` utility and its subcommands. It ensures global help, command help, missing arguments, unknown commands, and illegal options report usage consistently.

## Important APIs, Types, and Functions

The `commands` list covers most `wt` subcommands except `copyright`. Test methods are `test_help_option`, `test_no_argument`, `test_unsupported_command`, and `test_unsupported_option`.

## Control Flow

The tests run `wt -?`, each `<command> -?`, `wt -h`, an unsupported command, and `-^` both globally and per command. They inspect a shared stderr file for `global_options:`, `options:`, or exact illegal/missing option messages.

## State and Persistence Behavior

No data persistence is required; state is stderr output from the utility parser.

## Dependencies and Integration Points

Depends on `suite_subprocess`, global option parsing, command dispatch, and per-command usage generation.

## Risks and Edge Cases

Exact parser wording is asserted, and the static command list must be updated when supported commands change.

## Test Signals

Signals are successful help invocations, expected failure for invalid options, and correct distinction between global help text and command-specific options text.
