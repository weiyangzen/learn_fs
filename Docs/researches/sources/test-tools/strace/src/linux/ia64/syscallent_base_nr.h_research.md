<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/ia64/syscallent_base_nr.h -->
# sources/test-tools/strace/src/linux/ia64/syscallent_base_nr.h

## Purpose
Defines the architecture syscall table base offset used by the IA-64 backend.

## Important APIs, Types, and Functions
- `SYSCALLENT_BASE_NR` is set to `(1U << 10)`, matching IA-64's shifted syscall numbering convention used by `shuffle_scno.c` and `arch_defs_.h`.

## Control Flow
- No executable control flow; the macro is consumed at compile time when normalizing IA-64 syscall numbers and audit personality metadata.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `ia64`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- A wrong base value would desynchronize syscall table lookup from kernel syscall numbers, causing broad mis-decoding rather than isolated failures.

## Test Signals
- Build strace for `ia64` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/ia64/syscallent_base_nr.h`: 1 lines; 38 bytes; defines `#define SYSCALLENT_BASE_NR (1U << 10)`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/ia64/syscallent_base_nr.h -->
