# File Research: sources/local-fs/reiserfsprogs/resize_reiserfs/resize.h

Shared header for the resize utility.

Major responsibilities:
- Includes project configuration, I/O, misc, ReiserFS core library, and version banner definitions.
- Selects mount headers depending on glibc.
- Defines `print_usage_and_exit()` and `DIE()` utility macros.
- Declares resize globals: `g_sb_bh`, `g_progname`, option flags, and resize entry points.

Dependencies and interactions:
- Included by `resize_reiserfs.c`, `do_shrink.c`, and `fe.c`.
- Exposes `resize_fs_online()` and `shrink_fs()` across compilation units.
- Pulls `../version.h` for `print_banner()`.

Risks and notes:
- `print_usage_and_exit()` uses `argv[0]` from the including function scope, which works in `main()` but is macro-coupled.
- Uses GNU variadic macro syntax in `DIE()`.
