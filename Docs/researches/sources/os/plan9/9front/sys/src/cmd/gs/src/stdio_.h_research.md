# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/stdio_.h

Generic substitute for `stdio.h`.

Key points:
- Includes `std.h` before `<stdio.h>`.
- On old VMS, maps `unlink` to `delete`.
- Declares `unlink(const char *)` for systems where stdio may not provide it.
- On Plan 9, renames system `sclose` out of the way by mapping `sclose(s)` to `Sclose(s)` before Ghostscript’s stream `sclose`.
- Defines missing `SEEK_SET`, `SEEK_CUR`, and `SEEK_END`.
- Maps MSVC `fdopen` and `fileno` to underscored variants.

Dependencies and interactions:
- Important for `stream.h`/`stream.c`, where Ghostscript defines its own `sclose`.
- Used throughout code that needs stdio plus Ghostscript’s portability setup.

Research relevance:
- Contains a direct Plan 9 compatibility fix for a stream API name collision.
