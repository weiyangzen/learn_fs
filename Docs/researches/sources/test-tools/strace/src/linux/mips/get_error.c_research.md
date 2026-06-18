<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/get_error.c -->
# sources/test-tools/strace/src/linux/mips/get_error.c

## Purpose
Maps the `mips` syscall result registers into strace's normalized `tcp->u_rval` and `tcp->u_error` fields.

## Important APIs, Types, and Functions
- `arch_get_error(struct tcb *tcp, bool check_errno)` is the architecture hook called on syscall exit.
- mips_regs.uregs with v0 at index 2, a0 at index 4, a3 at index 7, stack at index 29, and PC at index 34
- MIPS uses dedicated error register semantics: `mips_REG_A3` indicates failure and `mips_REG_V0` carries the positive errno or success result.

## Control Flow
- On syscall exit, the helper inspects the ABI-specific error signal.
- Failure sets `tcp->u_rval = -1` and fills `tcp->u_error`; success stores the raw return value in `tcp->u_rval`.

## State and Persistence Behavior
- No persistent storage is owned here; it mutates the current `struct tcb` result fields based on the latest cached register snapshot.

## Dependencies and Integration Points
- Called by the generic syscall-exit path after register refresh.
- Depends on sibling `arch_regs.c` definitions, `negated_errno.h` where used, and shared `struct tcb` result conventions.

## Risks and Edge Cases
- `check_errno` and ABI-specific error flags must not be conflated; doing so makes large successful unsigned returns look like failures or hides real errors.
- The helper assumes the architecture register snapshot is fresh for the current syscall-exit stop.

## Test Signals
- Trace successful and failing syscalls on `mips` and compare printed return values and errno names.
- Include tests for large positive returns, negative errno returns, and ABI-specific dedicated error flags where applicable.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/mips/get_error.c`: 17 lines; 315 bytes; functions `arch_get_error`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/get_error.c -->
