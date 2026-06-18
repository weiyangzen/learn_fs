# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_unifn.c

Read status: complete.

Purpose: Unix-like filename syntax helpers for Ghostscript.

Main logic:
- Defines file-list separator `:`.
- Defines no binary mode suffix and text-equivalent modes `r` and `w`.
- `gp_file_name_root` recognizes `/` as root.
- `gs_file_name_check_separator` recognizes `/` forward and backward.
- Parent is `..`; current directory is `.`.
- Separators are `/`.
- Parent references are allowed; empty path items are not meaningful.
- `gp_file_name_combine` delegates to `gp_file_name_combine_generic`.

Filesystem/storage relevance:
- Provides Unix path syntax for Ghostscript file-name normalization and combination.
