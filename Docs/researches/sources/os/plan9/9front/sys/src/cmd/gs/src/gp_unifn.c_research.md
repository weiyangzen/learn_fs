# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_unifn.c

Unix-like filename syntax helpers.

Key behavior:
- Defines `:` as file-list separator.
- Defines no binary-mode suffix and uses `r`/`w` for binary read/write modes.
- Treats `/` as the root and path separator.
- Recognizes `..` as parent and `.` as current directory.
- Delegates full path combination to `gp_file_name_combine_generic`.

Research notes:
- This is path syntax glue for Unix-like platforms, not file I/O or enumeration.
