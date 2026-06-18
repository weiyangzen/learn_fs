# File Research: sources/local-fs/ntfs-3g/libntfs-3g/logging.c

## Purpose
Centralized logging framework for NTFS-3G library/tools, with configurable levels, style flags, and output handlers.

## Main Interfaces
- `ntfs_log_get_levels()`, `ntfs_log_set_levels()`, `ntfs_log_clear_levels()`.
- `ntfs_log_get_flags()`, `ntfs_log_set_flags()`, `ntfs_log_clear_flags()`.
- `ntfs_log_set_handler()` installs the active handler.
- `ntfs_log_redirect()` is the central varargs dispatcher used by logging macros.
- Handlers: `ntfs_log_handler_syslog()`, `ntfs_log_handler_fprintf()`, `ntfs_log_handler_null()`, `ntfs_log_handler_stdout()`, `ntfs_log_handler_outerr()`, `ntfs_log_handler_stderr()`.
- `ntfs_log_early_error()` logs before normal redirection.
- `ntfs_log_parse_option()` handles `--log-*` options.

## Control Flow
A static `ntfs_log` struct holds enabled levels, style flags, and handler. `ntfs_log_redirect()` preserves caller `errno`, filters disabled levels, invokes the handler, and restores `errno`. The fprintf handler applies optional filename, line, function, prefix, perror text, and debug indentation.

## Integration Points
Used throughout libntfs-3g via logging macros. Syslog integration is conditional on `HAVE_SYSLOG_H`.

## Risks and Invariants
- `errno` preservation is a key invariant.
- Non-debug syslog suppresses `ENOSPC` perror spam.
- Default handler is null in non-debug builds, outerr in debug builds.
- `ntfs_log_parse_option()` only recognizes debug, verbose, quiet, and trace options.
