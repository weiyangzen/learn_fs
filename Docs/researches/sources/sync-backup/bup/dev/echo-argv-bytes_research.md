# sources/sync-backup/bup/dev/echo-argv-bytes

## Purpose
Debug/test utility that writes argv byte values exactly, preserving non-text path encodings.

## Important APIs, Types, and Functions
Bootstraps `dev/bup-exec`, uses `bup.compat.get_argvb`, `os.write`, and stdout.

## Control Flow
Loops over argv bytes, writes each argument followed by `NUL` and newline, and flushes stdout.

## State and Persistence Behavior
No persistence; output is raw bytes.

## Dependencies and Integration Points
Supports tests for command-line byte handling and filesystem path encoding.

## Risks and Test Signals
Risks are stdout text wrapper interference avoided via `os.write`. Signal is byte-exact output including argv[0].
