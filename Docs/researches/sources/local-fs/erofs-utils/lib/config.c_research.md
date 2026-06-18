# File Research: sources/local-fs/erofs-utils/lib/config.c

## Purpose
Global configuration, logging, progress display, SELinux label handle lifecycle, root path trimming, and CPU count helper.

## Main Globals
- `struct erofs_configure cfg`: process-wide configuration.
- `struct erofs_sb_info g_sbi`: global superblock info used by many tools.
- `bool erofs_stdout_tty`: cached stdout TTY status.
- `fullpath_prefix`: prefix length for source-root-relative paths.

## Important Functions
- `erofs_init_configure()` / `erofs_exit_configure()`: initialize defaults and free config strings/SELinux handle.
- `erofs_show_config()`: debug dump.
- `erofs_get_configure()`: returns `&cfg`.
- `erofs_set_fs_root()` / `erofs_fspath()`: configure and compute relative filesystem paths.
- `erofs_selabel_open()`: optional SELinux file contexts setup.
- `erofs_trim_for_progressinfo()`: TTY-width-aware progress path shortening.
- `erofs_msg()`: common logging backend.
- `erofs_update_progressinfo()`: carriage-return progress display when enabled.
- `erofs_get_available_processors()`: returns online processor count when `sysconf` is available.

## Interactions
- Used throughout `liberofs` and tools for global config and logging.
- `global.c` wraps this with library-global init/exit.

## Notes
`erofs_update_progressinfo()` uses `vsprintf()` into an 8192-byte local buffer, assuming callers provide bounded messages.
