<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/ioctls_arch0.h -->
# sources/test-tools/strace/src/linux/mips/ioctls_arch0.h

## Purpose
Adds `mips`-specific ioctl decoder metadata that is not covered by the common generated ioctl include.

## Important APIs, Types, and Functions
- Rows contain header name, ioctl symbol, direction flags, request number, and encoded size. This file has 149 explicit rows.

## Control Flow
- No runtime branches; the compiled ioctl table is searched by the generic ioctl decoder.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `mips`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Request numbers and encoded sizes must match kernel UAPI for this architecture. Copying another architecture's ioctl rows can silently decode the wrong command or data size.

## Test Signals
- Build strace for `mips` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/mips/ioctls_arch0.h`: 150 lines; 8778 bytes; 149 ioctl table rows. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/ioctls_arch0.h -->
