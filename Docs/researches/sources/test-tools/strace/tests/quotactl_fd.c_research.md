<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl_fd.c -->
# sources/test-tools/strace/tests/quotactl_fd.c

## Purpose

This test covers the newer `quotactl_fd` syscall, including descriptor/path rendering variants. Source read: complete file, 84 lines, 1972 bytes, sha256 `8c0bb3d585e534af`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`, `"xmalloc.h"`, `<fcntl.h>`, `<stdio.h>`, `<stdlib.h>`, `<unistd.h>`, `<linux/quota.h>`, `"xlat.h"`, `"xlat/quota_formats.h"`. Compile-time macros: none found. Functions/helpers: `k_quotactl_fd`, `main`. Direct syscall numbers: `__NR_quotactl_fd`. Notable constants/xlats: `QCMD`, `Q_GETFMT`.

## Control Flow

It opens candidate files, invokes `__NR_quotactl_fd` through `k_quotactl_fd`, and prints expected command, file descriptor, quota id, format, and errno output. `-P` and `-y` wrappers enable path tracing or fd decoding and require `/proc/self/fd`.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; generated xlat tables and xlat formatting macros; kernel syscall availability for `__NR_quotactl_fd`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

`quotactl_fd` availability, `/proc` fd symlink availability, and descriptor decoding mode can alter expected traces.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl_fd.c -->
