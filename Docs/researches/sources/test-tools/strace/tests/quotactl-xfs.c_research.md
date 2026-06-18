<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl-xfs.c -->
# sources/test-tools/strace/tests/quotactl-xfs.c

## Purpose

This is the XFS quota `quotactl` decoder test. It targets XFS-specific subcommands and structures from `linux/dqblk_xfs.h`. Source read: complete file, 344 lines, 8808 bytes, sha256 `6efc5d76600bc42e`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`, `<stdio.h>`, `<string.h>`, `<unistd.h>`, `<linux/dqblk_xfs.h>`, `"quotactl.h"`, `"xlat.h"`, `"xlat/xfs_dqblk_flags.h"`. Compile-time macros: none found. Functions/helpers: `main`, `print_xdisk_quota`, `print_xquota_stat`, `print_xquota_statv`. Direct syscall numbers: none found. Notable constants/xlats: `QCMD`, `QCMD_TYPE`, `Q_XGETNEXTQUOTA`, `Q_XGETQSTAT`, `Q_XGETQSTATV`, `Q_XGETQUOTA`, `Q_XQUOTAOFF`, `Q_XQUOTAON`, `Q_XQUOTARM`, `Q_XQUOTASYNC`, `Q_XSETQLIM`.

## Control Flow

The test prints XFS disk quota, quota stat, and quota statv structures, then exercises XFS quota command variants through the common `check_quota` helper. `VERBOSE` builds include full structure payloads; success-injection wrappers force successful return formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; generated xlat tables and xlat formatting macros; shared quota test helper `quotactl.h`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

XFS quota struct shape, flag xlat tables, and verbose/non-verbose differences are the main sources of expected-output drift.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl-xfs.c -->
