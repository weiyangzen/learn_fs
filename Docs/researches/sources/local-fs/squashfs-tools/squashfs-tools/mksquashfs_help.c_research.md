# File Research: sources/local-fs/squashfs-tools/squashfs-tools/mksquashfs_help.c

Implements all help output for `mksquashfs` and `sqfstar`. It stores parallel arrays for option names, argument labels, section names, and long help text, covering compression, build, time, permissions, pseudo definitions, filters, xattrs, runtime, append, actions, tar, expert, help, misc, symbolic modes, environment, exit status, and external documentation links.

Core output paths use `launch_pager()` plus `autowrap_print()` from `print_pager.c`. `print_help_all()` emits full help and compressor usage. `print_option()` compiles a POSIX extended regex and matches against option names and argument labels. `print_section()` supports exact section names, `list`, and regex matching.

Public entry points are wrappers for each program: `mksquashfs_help_all`, `sqfstar_help_all`, option/section lookup, invalid-option handling, contextual option help, compressor listing, and compressor-specific option output.

Compile-time macros from `mksquashfs_help.h` alter displayed defaults for xattrs and reader thread configuration. Unsupported compressors are rejected with available compressor display before exiting.
