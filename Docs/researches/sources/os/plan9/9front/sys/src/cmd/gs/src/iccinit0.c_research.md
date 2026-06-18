# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iccinit0.c

Defines the non-compiled initialization string.

Key points:
- Includes `stdpre.h`.
- Exports `gs_init_string` as a single zero byte.
- Exports `gs_init_string_sizeof` as zero.
- Comment notes `gsmain.c` recognizes an empty init string specially.

Research notes:
- This is configuration data, not logic.
- It represents the build mode where initialization is not embedded as compiled PostScript content.
