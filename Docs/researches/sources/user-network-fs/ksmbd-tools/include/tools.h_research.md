<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/tools.h -->
# sources/user-network-fs/ksmbd-tools/include/tools.h

## Purpose

Common utility header for the ksmbd-tools multi-call binary, logging, paths, global configuration, charset conversion, Base64, config load/remove, and GLib hash iteration helpers.

## Important APIs, Types, and Functions

Defines `struct smbconf_global`, path constants, health flags, logging levels/macros, charset enum, tool dispatch declarations, helper functions such as `base64_encode`, `ksmbd_gconvert`, `set_conf_contents`, `load_config`, `remove_config`, `show_version`, and hash iteration macros.

## Control Flow

All CLIs use tool dispatch and logging; config load populates `global_conf`, parser, users, and shares; mountd uses health flags to reload/list/stop; adduser/addshare use string-array and config-write helpers.

## State and Persistence Behavior

Global state includes `global_conf`, `ksmbd_health_status`, `log_level`, and `tool_main`. Persistence is through `set_conf_contents` and the config/password files.

## Dependencies and Integration Points

Depends on GLib, POSIX process/signal I/O, generated config.h, and all component main functions.

## Risks and Edge Cases

Global mutable state limits reentrancy. Compile-time `SYSCONFDIR` and `RUNSTATEDIR` must match packaging/service files. Logging macros inject tool name and pid into every message.

## Test Signals

Tests should cover multi-call dispatch by argv name/symlink, config load/remove cycles, Base64 round trips, charset conversion, config atomic write behavior, and logging level filtering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/tools.h -->
