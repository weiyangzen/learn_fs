<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl.c -->
# sources/test-tools/strace/tests/quotactl.c

## Purpose

This is the Linux quota `quotactl` syscall decoder test. It exercises command composition, quota ids, device pointers, quota format values, and the structures returned by or passed to common quota commands. Source read: complete file, 390 lines, 9773 bytes, sha256 `2f7699325849049e`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`, `<inttypes.h>`, `<stdint.h>`, `<stdio.h>`, `<string.h>`, `<unistd.h>`, `"quotactl.h"`, `"xlat.h"`, `"xlat/quota_formats.h"`, `"xlat/if_dqblk_valid.h"`, `"xlat/if_dqinfo_flags.h"`, `"xlat/if_dqinfo_valid.h"`. Compile-time macros: `QUOTA_STR`, `QUOTA_ID_STR`, `QUOTA_STR_INVALID`. Functions/helpers: `gen_quotacmd`, `gen_quotaid`, `main`, `print_dqblk`, `print_dqfmt`, `print_dqinfo`, `print_nextdqblk`. Direct syscall numbers: none found. Notable constants/xlats: `QCMD`, `QCMD_CMD`, `QCMD_TYPE`, `Q_`, `Q_GETFMT`, `Q_GETINFO`, `Q_GETNEXTQUOTA`, `Q_GETQUOTA`, `Q_QUOTAOFF`, `Q_QUOTAON`, `Q_SETINFO`, `Q_SETQUOTA`, `Q_SYNC`.

## Control Flow

Helper functions generate human-readable `QCMD` and quota-id strings, print `if_dqblk`, `if_dqinfo`, `if_nextdqblk`, and quota-format payloads, and `main` calls shared `check_quota` cases from `quotactl.h` across valid, invalid, NULL, unterminated, verbose, raw, and injected-success scenarios.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; generated xlat tables and xlat formatting macros; shared quota test helper `quotactl.h`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

Quota command bit packing, host-header xlat availability, struct-field formatting, and injected-success behavior can all change expected traces.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl.c -->
