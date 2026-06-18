<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/or1k/get_error.c -->
# sources/test-tools/strace/src/linux/or1k/get_error.c

## Purpose
Maps the `or1k` syscall result registers into strace's normalized `tcp->u_rval` and `tcp->u_error` fields.

## Important APIs, Types, and Functions
- `arch_get_error(struct tcb *tcp, bool check_errno)` is the architecture hook called on syscall exit.
- user_regs_struct or1k_regs; syscall number gpr[11], return gpr[11], stack gpr[1], PC pc
- The helper decodes the architecture's result register and uses `is_negated_errno` when this ABI reports failures as negative return values.

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
- Trace successful and failing syscalls on `or1k` and compare printed return values and errno names.
- Include tests for large positive returns, negative errno returns, and ABI-specific dedicated error flags where applicable.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/or1k/get_error.c`: 19 lines; 395 bytes; includes `#include "negated_errno.h"`; functions `arch_get_error`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/or1k/get_error.c -->
