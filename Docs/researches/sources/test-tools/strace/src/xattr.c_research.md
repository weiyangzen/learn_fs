<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xattr.c -->
# sources/test-tools/strace/src/xattr.c

Purpose: Extended-attribute syscall decoder for path, fd, and modern `*xattrat` variants; prints names, values, list buffers, flags, and `struct xattr_args` payloads.

Important APIs/types/functions:
- SYS_FUNC handlers: `setxattr`, `fsetxattr`, `getxattr`, `fgetxattr`, `listxattr`, `flistxattr`, `removexattr`, `fremovexattr`, `setxattrat`, `getxattrat`, `listxattrat`, `removexattrat`
- Helper functions include `print_xattr_val`, `decode_setxattr_without_path`, `decode_getxattr_without_path`, `print_xattr_list`, `decode_dirfd_pathname_flags`, `decode_dirfd_pathname_flags_name`, `umove_xattr_args_or_printaddr`, `print_xattr_args`
- Direct includes: `"defs.h"`, `<linux/fcntl.h>`, `<linux/xattr.h>`, `"xlat/xattrflags.h"`, `"xlat/xattrat_flags.h"`
- Xlat tables consumed: `xattrflags`, `xattrat_flags`
- Local/exported macros: `XATTR_SIZE_MAX`

Control flow:
- uses strace two-phase syscall decoding, printing input-only fields on entry and result/output structures on exit when `syserror(tcp)` is false
- copies tracee memory defensively and falls back to raw addresses when data cannot be fetched
- stores entry-side values in per-tcb private data so exit-side decoding can show kernel-mutated fields

State and persistence behavior:
- per-syscall transient state is held on `struct tcb` private data between entry and exit
- uses static process-local configuration/cache data; no repository-persistent state is written

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers
- integrates generated `xlat/*` tables for symbolic constants

Risks:
- must tolerate invalid tracee pointers, short reads, and tracee mutation between entry and exit
- length/count fields need bounds-aware printing to avoid misleading output or excessive tracee reads

Test signals:
- expected test signals are strace output fixtures covering decoded names, raw fallback for unknown values, invalid-pointer paths, and successful exit-side structure decoding
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xattr.c -->
