<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl.h -->
# sources/test-tools/strace/tests/quotactl.h

## Purpose

This header centralizes shared Linux and XFS quota test machinery for `quotactl`-family tests. Source read: complete file, 204 lines, 7018 bytes, sha256 `6b99f8bbb23cf567`.

## Important APIs, Types, and Functions

Includes: none found. Compile-time macros: none found. Functions/helpers: `check_quota`. Direct syscall numbers: `__NR_quotactl`. Notable constants/xlats: `QCMD_CMD`, `QCMD_TYPE`.

## Control Flow

`check_quota` performs the direct `__NR_quotactl` syscall with command, id, device, and address arguments, captures `sprintrc`, and prints the expected trace line. It supports flag combinations controlling whether command bits, ids, device strings, addresses, and output strings are printed as raw, xlat, or verbose forms.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

kernel syscall availability for `__NR_quotactl`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

Because this header owns the shared expected-line contract, mistakes here would affect every quota wrapper in this subset.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl.h -->
