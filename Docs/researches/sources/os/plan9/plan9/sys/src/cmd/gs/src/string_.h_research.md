# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/string_.h

Purpose: Ghostscript wrapper around string/memory headers.

Key contents:
- Includes `std.h` first.
- Uses `<strings.h>` and maps `strchr` to `index` for `BSD4_2`.
- Otherwise includes `<string.h>`.
- Optionally replaces `memmove` with `gs_memmove` when `MEMORY__NEED_MEMMOVE` is set.
- Adjusts `strlen` for THINK C.

Dependencies: `std.h`, system string headers.

Integration notes: centralizes portability behavior for memory/string functions.

Risks: macro replacement of `memmove` must be consistent with memory subsystem configuration.
