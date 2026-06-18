<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/signalent.h -->
# sources/test-tools/strace/src/linux/mips/signalent.h

## Purpose
Defines the MIPS signal-number to signal-name table used by signal decoders.

## Important APIs, Types, and Functions
- The file is a string initializer array with Linux/MIPS signal names including architecture-specific real-time signal numbering conventions.

## Control Flow
- No executable control flow; consumers index the table by signal number.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `mips`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Off-by-one table edits or generic signal table reuse would make signal traces misleading, especially for SIGRT ranges and architecture-specific aliases.

## Test Signals
- Build strace for `mips` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/mips/signalent.h`: 40 lines; 801 bytes. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/signalent.h -->
