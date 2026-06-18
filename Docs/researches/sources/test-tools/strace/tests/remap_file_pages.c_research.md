<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/remap_file_pages.c -->
# sources/test-tools/strace/tests/remap_file_pages.c

## Purpose

`sources/test-tools/strace/tests/remap_file_pages.c` checks `remap_file_pages` syscall decoding for address, size, protection, pgoff, and map flags in the strace tests tree. Source read: complete file, 115 lines, 3664 bytes, sha256 `ef5279ba01890375`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`, `<stdio.h>`, `<stdint.h>`, `<unistd.h>`, `<linux/mman.h>`. Compile-time macros: `prot1_str`, `flags1_str`. Functions/helpers: `k_remap_file_pages`, `main`. Direct syscall numbers: `__NR_remap_file_pages`. Notable constants/xlats: `MAP_`, `MAP_ANONYMOUS`, `MAP_FIXED`, `MAP_HUGETLB`, `MAP_HUGE_2MB`, `MAP_HUGE_SHIFT`, `MAP_NORESERVE`, `MAP_PRIVATE`, `MAP_SHARED_VALIDATE`, `MAP_TYPE`, `PROT_`, `PROT_EXEC`, `PROT_NONE`, `PROT_READ`, `PROT_WRITE`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_remap_file_pages` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `k_remap_file_pages`, `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_remap_file_pages`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/remap_file_pages.c -->
