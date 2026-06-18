# File Research: sources/os/linux/linux/fs/xfs/xfs_message.h

## Purpose

`xfs_message.h` declares XFS message and assertion interfaces and defines the severity macros used throughout XFS.

## Main Responsibilities

- Define `xfs_emerg`, `xfs_alert`, `xfs_crit`, `xfs_err`, `xfs_warn`, `xfs_notice`, `xfs_info`, and debug variants.
- Integrate printk indexing through `printk_index_subsys_emit`.
- Provide rate-limited and once-only wrappers around the severity macros.
- Declare assertion handlers, hex dump support, buffer-alert support, and experimental feature warning support.

## Important Interfaces

- `xfs_printk_level`: severity-level backend.
- `xfs_alert_tag`: indexed alert wrapper that calls `_xfs_alert_tag`.
- `xfs_printk_ratelimited`: local static ratelimit wrapper macro.
- `xfs_printk_once`: `DO_ONCE_LITE` wrapper.
- `assfail` and `asswarn`: assertion backends used by `xfs_platform.h`.
- `xfs_buf_alert_ratelimited`: per-buffer-target alert path.
- `enum xfs_experimental_feat`: enumerates experimental feature warnings.

## Conditional Behavior

`xfs_debug` emits only in `DEBUG` builds. In non-debug builds, it compiles to an empty statement. `xfs_debug_ratelimited` still resolves through the debug macro and therefore inherits that behavior.

## Dependencies

Includes `linux/once_lite.h` and forward-declares `struct xfs_mount`.
