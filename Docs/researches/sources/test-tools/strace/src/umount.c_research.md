<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/umount.c -->
# sources/test-tools/strace/src/umount.c

Purpose: Decoder for `umount2`, printing the target path and symbolic mount-detach/force/expire/no-follow flags.

Important APIs/types/functions:
- SYS_FUNC handlers: `umount2`
- Direct includes: `"defs.h"`, `"xlat/umount_flags.h"`
- Xlat tables consumed: `umount_flags`

Control flow:
- control flow is linear around a small decoder/helper surface and returns standard strace `RVAL_*` flags

State and persistence behavior:
- no persistent storage; behavior is derived from current tracee arguments, return value, and build-time headers

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers
- integrates generated `xlat/*` tables for symbolic constants

Risks:
- main risk is semantic drift when syscall ABI or generated xlat definitions change

Test signals:
- expected test signals are strace output fixtures covering decoded names, raw fallback for unknown values, invalid-pointer paths, and successful exit-side structure decoding
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/umount.c -->
