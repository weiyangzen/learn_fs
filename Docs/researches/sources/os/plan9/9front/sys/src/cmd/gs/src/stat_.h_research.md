# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/stat_.h

Generic substitute for Unix `sys/stat.h`.

Key points:
- Includes `std.h` before any header that may include `sys/types.h`.
- Includes `<stat.h>` for Metrowerks, otherwise `<sys/stat.h>`.
- Defines `stat_blocks(psbuf)` with a Plan 9-inclusive fallback based on file size when `st_blocks` is unavailable.
- Maps Microsoft `_stat` to `stat`.
- Provides `stat_is_dir(stbuf)` across systems with or without `S_ISDIR`.
- Patches `S_ISCHR`, `S_ISREG`, `S_IRUSR`, and `S_IWUSR` when missing.

Dependencies and interactions:
- Used by Ghostscript platform/file code needing portable stat metadata.
- Plan 9 is explicitly handled in the no-`st_blocks` platform list.

Research relevance:
- This is portability glue that normalizes filesystem metadata tests across Unix, Plan 9, Windows, VMS, and older compilers.
