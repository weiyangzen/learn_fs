<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/userent.h -->
# sources/test-tools/strace/src/linux/mips/userent.h

## Purpose
Provides the ptrace user-area offset to register-name table for strace's `mips` register printers.

## Important APIs, Types, and Functions
- The file contributes initializer rows of `{ offset, name }` pairs and may include `userent0.h` for common trailing entries.
- Rows cover architecture-visible register offsets; source facts show 71 explicit offset/name entries.

## Control Flow
- There is no runtime branch logic; generic user-area decoding iterates the compiled table when printing PTRACE_PEEKUSER-style offsets.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `mips`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Offsets must match kernel UAPI headers for the exact architecture ABI; stale offsets produce plausible-looking but wrong register names.

## Test Signals
- Build strace for `mips` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/mips/userent.h`: 90 lines; 1582 bytes; includes `#include "userent0.h"`; 71 ptrace user offset/name rows. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/userent.h -->
