<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/errnoent.h -->
# sources/test-tools/strace/src/linux/mips/errnoent.h

## Purpose
Defines architecture errno name ordering for `mips` when it differs from the generic strace errno table.

## Important APIs, Types, and Functions
- The header is a data initializer consumed by strace errno/xlat infrastructure; PowerPC delegates to `../generic/errnoent.h`, while MIPS carries a full ABI-specific list.

## Control Flow
- No runtime control flow in the file; lookup is table-driven by the core errno decoder.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `mips`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- The numeric position of each string is the ABI contract. Insertions, deletions, or accidental generic substitution can make every later errno decode wrong.

## Test Signals
- Build strace for `mips` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/mips/errnoent.h`: 158 lines; 3133 bytes. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/errnoent.h -->
