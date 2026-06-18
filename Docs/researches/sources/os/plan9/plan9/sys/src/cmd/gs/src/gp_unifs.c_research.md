# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_unifs.c

Purpose: Implements Unix-like filesystem support routines for Ghostscript: scratch-file creation, binary/text stream handling, and wildcard file enumeration over POSIX directories.

Key interfaces: `gp_scratch_file_name_prefix`, `gp_null_file_name`, `gp_current_directory_name`, `gp_open_scratch_file`, `gp_fopen`, `gp_setmode_binary`, `gp_enumerate_files_init`, `gp_enumerate_files_next`, and `gp_enumerate_files_close`.

Control flow: scratch-file creation combines an absolute prefix or temp directory from `gp_gettmpdir`, appends a safe template, then uses `mkstemp` when available or `mktemp` plus `gp_fopentemp` otherwise. Enumeration stores the original pattern and mutable work path in GC-managed memory, opens directories lazily, matches path segments with `string_match`, recursively descends through matching directories using a `dirstack`, and unwinds/cleans state on exhaustion.

Dependencies: Uses Ghostscript memory/GC descriptors, `gp.h`, `gpmisc.h`, `gsutil.h`, POSIX `opendir/readdir/closedir/stat`, and fallback path-length handling around `FILENAME_MAX`.

Risks and notes: The `mkstemp` failure check uses `file < -1`, which will not catch normal `-1` failure. The non-`mkstemp` fallback relies on `mktemp`, though `gp_fopentemp` mitigates race/symlink risk with `O_EXCL`. Allocation failures during enumeration initialization can leak earlier allocations because the partially allocated `file_enum` is not fully cleaned before returning.
