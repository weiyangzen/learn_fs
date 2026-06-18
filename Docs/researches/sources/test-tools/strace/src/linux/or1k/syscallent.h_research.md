<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/or1k/syscallent.h -->
# sources/test-tools/strace/src/linux/or1k/syscallent.h

## Purpose
Defines the `or1k` syscall dispatch table rows consumed by strace's syscall decoder.

## Important APIs, Types, and Functions
- The table contains indexed rows with argument count, flags, `SEN(decoder)` handler, and printable syscall name. It references 1 decoder entries; first entries include or1k_atomic; final entries include or1k_atomic.

## Control Flow
- The file itself is declarative; runtime flow is in the generic syscall dispatch path, which indexes `sysent` by normalized syscall number, then calls the selected `SEN(...)` decoder.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `or1k`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Index placement, ABI base numbers, and included common tables are the main risk. One shifted row causes wrong names, qualifiers, argument counts, and decoder selection.

## Test Signals
- Build strace for `or1k` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/or1k/syscallent.h`: 11 lines; 288 bytes; includes `#include "../32/syscallent.h"`; defines `#define sys_ARCH_mmap sys_mmap_pgoff`; 1 `SEN(...)` syscall decoder references; first or1k_atomic; last or1k_atomic. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/or1k/syscallent.h -->
