# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/stdio_.h

Purpose: Ghostscript wrapper around standard I/O headers.

Key contents:
- Includes `std.h` before `<stdio.h>` to avoid `sys/types.h` ordering conflicts.
- Supplies or remaps `unlink` on older VMS and non-VMS systems.
- Contains Plan 9-specific protection against a system `sclose` name collision by redefining `sclose(s)` to `Sclose(s)` when `Plan9` is set.
- Defines missing `SEEK_SET`, `SEEK_CUR`, and `SEEK_END`.
- Maps MSVC `fdopen`/`fileno` to underscored CRT names.

Dependencies: `std.h`, `<stdio.h>`, optional VMS `<unixio.h>`.

Integration notes: `stream.c` includes this file before the stream package, so the Plan 9 `sclose` collision handling is directly relevant.

Risks: macro remapping of `sclose` changes symbol visibility and must match how the Plan 9 port compiles system headers versus Ghostscript stream APIs.
