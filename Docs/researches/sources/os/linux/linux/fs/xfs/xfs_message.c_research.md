# File Research: sources/os/linux/linux/fs/xfs/xfs_message.c

## Purpose

`xfs_message.c` implements XFS logging and assertion-message helpers. It centralizes printk formatting for mount-aware XFS messages, panic-mask alert escalation, assertion handling, hex dumps, buffer-specific rate-limited alerts, and experimental-feature warnings.

## Main Responsibilities

- Format messages as `XFS (<sb id>): ...` when a mount and superblock are available.
- Emit generic `XFS: ...` messages when no mount context exists.
- Trigger stack traces for high error verbosity on error-or-worse log levels.
- Convert selected alert tags into `BUG()` paths via `xfs_panic_mask`.
- Provide `asswarn` and `assfail` backends for XFS assertions.
- Provide `xfs_hex_dump`.
- Rate-limit buffer alerts using the buffer target’s I/O error ratelimit state.
- Warn once per mount for experimental features.

## Important Functions

- `__xfs_printk`: private formatter that chooses mount-specific or generic prefix.
- `xfs_printk_level`: varargs printk wrapper used by severity macros in `xfs_message.h`.
- `_xfs_alert_tag`: alert wrapper that can transform configured panic tags into `BUG_ON`.
- `asswarn`: warning assertion backend using `xfs_warn` and `WARN_ON`.
- `assfail`: fatal assertion backend using `xfs_emerg` and either `BUG()` or `WARN_ON`, depending on `xfs_globals.bug_on_assert`.
- `xfs_buf_alert_ratelimited`: emits buffer-target rate-limited alerts.
- `xfs_warn_experimental`: warns once for online shrink, logged extended attributes, or zoned RT device experimental features.

## External Dependencies

The file uses `xfs_mount`, `xfs_error_level`, `xfs_panic_mask`, `xfs_globals`, mount opstate warning bits, kernel printk, rate limiting, and hex dump facilities.

## Notes

The implementation intentionally keeps severity-specific public interfaces in the header as macros while centralizing varargs handling and mount-prefix formatting here.
