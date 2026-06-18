<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/loongarch64/ioctls_inc0.h -->
# sources/test-tools/strace/src/linux/loongarch64/ioctls_inc0.h

## Purpose
Selects the shared generated ioctl include set for the `loongarch64` personality.

## Important APIs, Types, and Functions
- The header includes the shared `../32/ioctls_inc.h` or `../64/ioctls_inc.h` file according to the architecture word size.

## Control Flow
- No executable code; it is a build-time composition point for the generated ioctl table.

## State and Persistence Behavior
- The data is immutable after compilation; persistent trace state lives in `struct tcb` fields such as `scno`, `true_scno`, `u_arg`, `u_rval`, and `u_error`.
- Generated or hand-maintained rows are integration state: correctness depends on staying synchronized with Linux UAPI syscall, errno, signal, ioctl, and ptrace-offset definitions.

## Dependencies and Integration Points
- Integrated by the strace Linux architecture backend for `loongarch64`.
- Depends on shared table macros such as `SEN`, syscall flags, `syscallent-common.h`, common 32/64-bit include files, or kernel UAPI constants depending on file role.

## Risks and Edge Cases
- Including the wrong word-size table changes encoded ioctl sizes and can break decoding for structures whose layout differs between 32-bit and 64-bit ABIs.

## Test Signals
- Build strace for `loongarch64` and compile with table warnings enabled.
- Compare decoded syscall/ioctl/errno/signal/register names against kernel headers and known trace samples.
- For syscall tables, trace boundary syscalls near architecture-specific ranges and newly added syscalls such as `statx`, `rseq`, and time64 variants where present.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/loongarch64/ioctls_inc0.h`: 1 lines; 30 bytes; includes `#include "../64/ioctls_inc.h"`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/loongarch64/ioctls_inc0.h -->
