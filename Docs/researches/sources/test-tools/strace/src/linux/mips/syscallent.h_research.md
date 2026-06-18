<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/syscallent.h -->
# sources/test-tools/strace/src/linux/mips/syscallent.h

## Purpose
Defines the `mips` syscall dispatch table rows consumed by strace's syscall decoder.

## Important APIs, Types, and Functions
- This wrapper composes one or more shared or ABI-specific syscall tables using `#include` directives rather than listing all rows inline.

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
Reviewed the complete local source file `sources/test-tools/strace/src/linux/mips/syscallent.h`: 4 lines; 115 bytes; includes `#include "syscallent-compat.h"`, `#include "syscallent-o32.h"`, `#include "syscallent-n64.h"`, `#include "syscallent-n32.h"`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/syscallent.h -->
