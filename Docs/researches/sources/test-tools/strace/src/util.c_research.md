<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/util.c -->
# sources/test-tools/strace/src/util.c

Purpose: Core utility layer for strace formatting, tracee-memory fetching, path/string/number printing, SELinux context helpers, timestamp math, iovec decoding, and process-control support used by many syscall decoders.

Important APIs/types/functions:
- Helper functions include `find_xlat_val_ex`, `find_arg_val_`, `str2timescale_ex`, `ts_nz`, `ts_cmp`, `ts_float`, `ts_add`, `ts_sub`, `ts_div`, `ts_min`, `ts_max`, `parse_ts`, `ilog10`, `print_ticks`, `print_ticks_d`, `print_clock_t`, `stpcpy`, `next_set_bit`...
- Direct includes: `"defs.h"`, `<limits.h>`, `<fcntl.h>`, `<stdarg.h>`, `<sys/stat.h>`, `<sys/sysmacros.h>`, `<sys/xattr.h>`, `<sys/uio.h>`, `"largefile_wrappers.h"`, `"number_set.h"`, `"print_fields.h"`, `"print_utils.h"`, `"secontext.h"`, `"static_assert.h"`, `"string_to_uint.h"`, `"xlat.h"`...
- Local/exported macros: `ILOG10_ITER_`, `DEF_PRINTNUM`, `DEF_PRINTNUM_ADDR`, `DEF_PRINTPAIR`, `ALLOCA_CUTOFF`, `use_alloca`, `iov`, `sizeof_iov`, `iov_iov_base`, `iov_iov_len`, `sizeof_iov`, `iov_iov_base`...

Control flow:
- uses strace two-phase syscall decoding, printing input-only fields on entry and result/output structures on exit when `syserror(tcp)` is false
- copies tracee memory defensively and falls back to raw addresses when data cannot be fetched
- dispatches switch cases such as `S_IFBLK`, `S_IFCHR`, `FINFO_DEV_BLK`, `FINFO_DEV_CHR`
- iterates user-provided arrays with bounded element fetch callbacks

State and persistence behavior:
- allocates temporary or per-tracee memory and releases it through explicit cleanup paths or tcb destructors
- uses static process-local configuration/cache data; no repository-persistent state is written

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers

Risks:
- must tolerate invalid tracee pointers, short reads, and tracee mutation between entry and exit
- length/count fields need bounds-aware printing to avoid misleading output or excessive tracee reads
- kernel/userspace structure layout drift is guarded by build-time assertions but still needs architecture coverage
- new kernel constants/ioctls require xlat/table and switch updates to keep symbolic output current

Test signals:
- expected test signals are strace output fixtures covering decoded names, raw fallback for unknown values, invalid-pointer paths, and successful exit-side structure decoding
- cover verbose versus abbreviated output modes
- cover raw, abbrev, and verbose xlat styles
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/util.c -->
