<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/userfaultfd.c -->
# sources/test-tools/strace/src/userfaultfd.c

Purpose: Decoder for the `userfaultfd` syscall and its ioctl protocol, including API negotiation, range operations, copy/zeropage/continue/poison results, and write-protect/register flags.

Important APIs/types/functions:
- SYS_FUNC handlers: `userfaultfd`
- Helper functions include `tprintf_uffdio_range`, `uffdio_ioctl`
- Direct includes: `"defs.h"`, `"kernel_fcntl.h"`, `<linux/ioctl.h>`, `<linux/userfaultfd.h>`, `"xlat/uffd_flags.h"`, `"xlat/uffd_api_features.h"`, `"xlat/uffd_api_flags.h"`, `"xlat/uffd_continue_mode_flags.h"`, `"xlat/uffd_copy_flags.h"`, `"xlat/uffd_poison_mode_flags.h"`, `"xlat/uffd_register_ioctl_flags.h"`, `"xlat/uffd_register_mode_flags.h"`, `"xlat/uffd_writeprotect_mode_flags.h"`, `"xlat/uffd_zeropage_flags.h"`
- Xlat tables consumed: `uffd_flags`, `uffd_api_features`, `uffd_api_flags`, `uffd_continue_mode_flags`, `uffd_copy_flags`, `uffd_poison_mode_flags`, `uffd_register_ioctl_flags`, `uffd_register_mode_flags`, `uffd_writeprotect_mode_flags`, `uffd_zeropage_flags`

Control flow:
- uses strace two-phase syscall decoding, printing input-only fields on entry and result/output structures on exit when `syserror(tcp)` is false
- copies tracee memory defensively and falls back to raw addresses when data cannot be fetched
- dispatches switch cases such as `UFFDIO_API`, `UFFDIO_COPY`, `UFFDIO_REGISTER`, `UFFDIO_UNREGISTER`, `UFFDIO_WAKE`, `UFFDIO_ZEROPAGE`, `UFFDIO_WRITEPROTECT`, `UFFDIO_CONTINUE`, `UFFDIO_POISON`
- stores entry-side values in per-tcb private data so exit-side decoding can show kernel-mutated fields

State and persistence behavior:
- per-syscall transient state is held on `struct tcb` private data between entry and exit
- allocates temporary or per-tracee memory and releases it through explicit cleanup paths or tcb destructors
- uses static process-local configuration/cache data; no repository-persistent state is written

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers
- integrates generated `xlat/*` tables for symbolic constants

Risks:
- must tolerate invalid tracee pointers, short reads, and tracee mutation between entry and exit
- length/count fields need bounds-aware printing to avoid misleading output or excessive tracee reads
- new kernel constants/ioctls require xlat/table and switch updates to keep symbolic output current

Test signals:
- expected test signals are strace output fixtures covering decoded names, raw fallback for unknown values, invalid-pointer paths, and successful exit-side structure decoding
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/userfaultfd.c -->
