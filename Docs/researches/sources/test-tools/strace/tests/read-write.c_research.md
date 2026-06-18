<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/read-write.c -->
# sources/test-tools/strace/tests/read-write.c

## Purpose

This test validates read/write syscall decoding and byte dumping behavior. Source read: complete file, 294 lines, 7093 bytes, sha256 `124a05ab32ae0326`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `<fcntl.h>`, `<stdio.h>`, `<stdlib.h>`, `<unistd.h>`, `"scno.h"`. Compile-time macros: none found. Functions/helpers: `dump_str`, `dump_str_ex`, `k_read`, `k_write`, `main`, `print_hex`, `test_dump`. Direct syscall numbers: `__NR_read`, `__NR_write`. Notable constants/xlats: none found.

## Control Flow

It uses direct `__NR_read`/`__NR_write`, helper printers for hex/escaped strings, and fixture data to check normal strings, truncated dump output, failed reads/writes, and printable/non-printable byte formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_read`, `__NR_write`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

Dump length options, string escaping, partial read/write behavior, and fd availability are the key regression surfaces.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/read-write.c -->
