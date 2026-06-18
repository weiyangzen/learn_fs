# File Research: sources/virtualization/libguestfs/daemon/cpmv.c

Implements simple `cp`, `cp -a`, `cp -rP`, and `mv` wrappers.

Key points:
- Guest paths are converted to sysroot paths before invoking external commands.
- `cpmv_cmd` centralizes command construction and error handling.
- Uses pulse-mode progress around external copy/move commands.
- `do_cp`, `do_cp_a`, `do_cp_r`, and `do_mv` differ only by command/flags.
