# File Research: sources/local-fs/squashfs-tools/squashfs-tools/mksquashfs_error.h

Defines mksquashfs-specific reporting macros layered on `error.h` and progress-bar control. `INFO` emits file information either to `info_file` or via `progressbar_info()` when `display_info` is enabled.

`ERROR_START` disables the progress bar before writing to stderr. `ERROR_EXIT` either exits through `EXIT_MKSQUASHFS()` when `exit_on_error` is set, or prints a suffix and re-enables the progress bar.

`EXIT_MKSQUASHFS()` calls `prep_exit()` before `exit(1)`, making fatal exits cleanup-aware.
