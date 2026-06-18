# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_unifs.c

Purpose: Unix-like filesystem platform layer for Ghostscript.

Key behavior: Defines Unix defaults for scratch prefix, `/dev/null`, and current directory. `gp_open_scratch_file` builds a temporary pathname from an absolute prefix or `gp_gettmpdir`, falls back to `/tmp/`, appends `XXXXXX`, and uses `mkstemp` when available or `mktemp` plus `gp_fopentemp` otherwise. `gp_fopen` is a direct `fopen`, and `gp_setmode_binary` is a no-op.

File enumeration: Implements `gp_enumerate_files_init/next/close` using `opendir`, `readdir`, `stat`, and a GC-visible `dirstack`. It rejects overlong and NUL-containing patterns, truncates the working path after the first wildcard directory segment, walks directories depth-first, skips `.` and `..`, uses `string_match`, and returns `~(uint)0` when enumeration is exhausted or cannot start.

Dependencies and notes: Uses Ghostscript memory descriptors for `file_enum` and `dirstack`, plus `gpmisc.h` temp/path helpers. Important edge cases are FILENAME_MAX normalization, root-directory handling, recursive wildcard path segments, and stack cleanup on enumeration close.
