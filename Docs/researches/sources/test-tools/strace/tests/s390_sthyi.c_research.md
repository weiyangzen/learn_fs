<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/s390_sthyi.c -->
# sources/test-tools/strace/tests/s390_sthyi.c

## Purpose

This s390-specific test validates decoding of the `s390_sthyi` syscall and its nested Store Hypervisor Information data block. Source read: complete file, 845 lines, 20512 bytes, sha256 `9890181aae7d31f5`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`. Compile-time macros: none found. Functions/helpers: `ebcdic2ascii`, `is_empty`, `main`, `print_0x8`, `print_ebcdic`, `print_funcs`, `print_guest_header`, `print_hypervisor_header`, `print_sthyi`, `print_u16`, `print_u8`, `print_weight`, `print_x32`. Direct syscall numbers: `__NR_s390_sthyi`. Notable constants/xlats: `STHYI`, `STHYI_FC_`, `STHYI_FC_CP_IFL_CAP`.

## Control Flow

When iconv and the syscall are available, helper printers decode EBCDIC fields, weights, CPU counts, partition/group/header fields, function codes, and reserved/empty blocks. `main` builds representative buffers, invokes `__NR_s390_sthyi`, and compares concise versus verbose output.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_s390_sthyi`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

The test depends on s390 UAPI layout, iconv availability, EBCDIC conversion, and verbose output stability across reserved fields.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/s390_sthyi.c -->
