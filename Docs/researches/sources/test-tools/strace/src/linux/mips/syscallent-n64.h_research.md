<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/syscallent-n64.h -->
# sources/test-tools/strace/src/linux/mips/syscallent-n64.h

## Purpose
Defines the `mips` syscall dispatch table rows consumed by strace's syscall decoder.

## Important APIs, Types, and Functions
- The table contains indexed rows with argument count, flags, `SEN(decoder)` handler, and printable syscall name. It references 328 decoder entries; first entries include read, write, open, close, stat, fstat; final entries include pkey_mprotect, pkey_alloc, pkey_free, statx, rseq, io_pgetevents_time64.

## Control Flow
- The file itself is declarative; runtime flow is in the generic syscall dispatch path, which indexes `sysent` by normalized syscall number, then calls the selected `SEN(...)` decoder.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `mips`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Index placement, ABI base numbers, and included common tables are the main risk. One shifted row causes wrong names, qualifiers, argument counts, and decoder selection.

## Test Signals
- Build strace for `mips` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/mips/syscallent-n64.h`: 353 lines; 20884 bytes; includes `# include "syscallent-common.h"`, `# include "../64/subcallent.h"`, `# include "syscallent-n64-stub.h"`, `# include "syscallent-common-stub.h"`; defines `#define BASE_NR 5000`, `# define SYS_socket_subcall      5500`, `# define SYSCALL_NAME_PREFIX "n64:"`, `#undef BASE_NR`; 328 `SEN(...)` syscall decoder references; first read, write, open, close; last pkey_free, statx, rseq, io_pgetevents_time64. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/syscallent-n64.h -->
