# sources/test-tools/ltp/testcases/kernel/syscalls/renameat2/renameat2.h

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/renameat2/renameat2.h` is a 35-line LTP source file in the `renameat2` syscall test area. renameat2 flag-specific rename coverage for RENAME_NOREPLACE and RENAME_EXCHANGE plus filesystem support differences.

## Important APIs, Types, and Functions

called APIs/macros: `renameat2`; local functions: `renameat2`; important macros/constants: `RENAMEAT2_H`.

## Control Flow

Function-level flow is organized around `renameat2`.

## State and Persistence Behavior

State is process-local test state: descriptors, buffers, errno/TST_RET values, and temporary resources managed by the LTP harness.

## Dependencies and Integration Points

Direct includes: `<sys/types.h>`, `"config.h"`, `"lapi/syscalls.h"`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations. Compile-time feature guards gate optional kernel/libc interfaces.

## Risks and Edge Cases

renameat2 tests depend on syscall and filesystem flag support; filesystems that do not implement exchange/noreplace semantics must be detected cleanly.

## Test Signals

Build and LTP result output are the primary test signals.
