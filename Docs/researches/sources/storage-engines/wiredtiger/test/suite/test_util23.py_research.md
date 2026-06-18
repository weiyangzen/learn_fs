# sources/storage-engines/wiredtiger/test/suite/test_util23.py

## Purpose

`test_util23.py` is a regression test for `wt verify` usage-path scratch-buffer handling. It verifies that a deliberately invalid command path reports usage without leaking a diagnostic scratch-buffer warning.

## Important APIs, Types, and Functions

The class defines `uri='file:test_util23.wt'`, command list `["-r", "verify", "-d", "dump_offsets", uri]`, and `test_verify_scratch_buffer`. It is skipped for the disaggregated hook because read-only utility connections are unsupported there.

## Control Flow

The test creates a file object, runs the command expecting failure, checks `errfile.txt` contains `usage:`, then reads the whole error file and asserts it does not contain `scratch buffer allocated and never discarded`.

## State and Persistence Behavior

The only persistent database state is the created file object; the main observed state is stderr from the utility failure path.

## Dependencies and Integration Points

Depends on `wt verify` option parsing, read-only `-r` global handling, diagnostics around scratch buffers, and `suite_subprocess`.

## Risks and Edge Cases

It is narrow and aimed at one leak diagnostic. It does not validate successful verify behavior.

## Test Signals

Expected signals are command failure with usage output and absence of the scratch-buffer diagnostic string.
