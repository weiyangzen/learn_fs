<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/udmabuf.c -->
# sources/test-tools/strace/src/udmabuf.c

Purpose: udmabuf ioctl decoder for `UDMABUF_CREATE` and `UDMABUF_CREATE_LIST`; it prints memfd-backed buffer creation structures, flags, offsets, sizes, and list entries.

Important APIs/types/functions:
- Helper functions include `print_udmabuf_create`, `print_udmabuf_create_item`, `print_udmabuf_create_list`, `udmabuf_ioctl`
- Direct includes: `"defs.h"`, `<linux/udmabuf.h>`, `"xlat/udmabuf_flags.h"`
- Xlat tables consumed: `udmabuf_flags`

Control flow:
- copies tracee memory defensively and falls back to raw addresses when data cannot be fetched
- dispatches switch cases such as `UDMABUF_CREATE`, `UDMABUF_CREATE_LIST`
- iterates user-provided arrays with bounded element fetch callbacks

State and persistence behavior:
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
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/udmabuf.c -->
