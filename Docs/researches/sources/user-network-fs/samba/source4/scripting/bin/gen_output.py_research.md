<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/gen_output.py -->
# sources/user-network-fs/samba/source4/scripting/bin/gen_output.py

## Purpose

`gen_output.py` is a small test utility that emits repeated data to stdout and exits with a caller-selected status code.

## Important APIs, Types, and Functions

It uses `argparse` options `--data`, `--repeat`, and `--retcode`, then writes `args.data * args.repeat` to stdout.

## Control Flow

The script parses arguments, writes the repeated data string, and exits with the requested return code.

## State and Persistence Behavior

No state is persisted. Output volume is controlled entirely by arguments.

## Dependencies and Integration Points

It depends only on Python standard library modules and is designed for tests that need large stdout/stderr-like data or nonzero command exits.

## Risks and Edge Cases

Very large repeat values allocate and write a large Python string, which can consume memory. Negative repeat values produce an empty string under Python string multiplication. Non-integer values are rejected by argparse.

## Test Signals

Tests should check default 1 MiB output, custom data, zero and negative repeat behavior, and nonzero exit code propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/gen_output.py -->
