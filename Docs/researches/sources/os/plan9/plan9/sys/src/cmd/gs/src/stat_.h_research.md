# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/stat_.h

Portable wrapper/substitute header around Unix `sys/stat.h`.

Key behavior:
- Includes `std.h` before platform stat headers to satisfy systems where `sys/types.h` ordering matters.
- Includes `<stat.h>` for Metrowerks, otherwise `<sys/stat.h>`.
- Defines `stat_blocks` using `st_blocks` where available, or approximates blocks from file size for many platforms including Plan9.
- Maps Microsoft `_stat` to `stat`.
- Defines `stat_is_dir` using `S_ISDIR` when available or mode-bit fallbacks otherwise.
- Defines missing `S_ISCHR`, `S_ISREG`, `S_IRUSR`, and `S_IWUSR` portability macros.

Notable dependencies:
- Platform/compiler preprocessor symbols.

Research notes:
- This is portability infrastructure rather than filesystem logic.
- Plan9 is explicitly included in the `stat_blocks` fallback path because its stat structure lacks portable `st_blocks`.
