# sources/user-network-fs/ksmbd-tools/tools/tools.c

## Purpose

`tools.c` is the shared entry point and utility layer for ksmbd-tools. It dispatches `ksmbd.tools` behavior by executable basename, owns logging selection, exposes charset/base64/string helpers, loads and removes global configuration state, initializes mountd subsystems, and prints version information. The source was read as a complete 381-line file.

## Important APIs, Types, and Functions

Public/shared functions include `__pr_log`, `pr_logger_init`, `set_log_level`, `pr_hex_dump`, `base64_encode`, `base64_decode`, `ksmbd_gconvert`, `gptrarray_to_strv`, `gptrarray_to_str`, `gptrarray_printf`, `set_conf_contents`, `load_config`, `remove_config`, `set_tool_main`, `get_tool_name`, `show_version`, and `main`. Global variables are `log_level`, `ksmbd_health_status`, and `tool_main`.

## Control Flow

`main` derives the basename and calls `set_tool_main`, which selects addshare, adduser, control, or mountd. `load_config` initializes user/share state, parses password and SMB config, and, for mountd, initializes sessions, RPC, IPC, SPNEGO, and worker pool. `remove_config` tears these down in reverse. Logging defaults to stdio and can switch to syslog.

## State and Persistence Behavior

Process state includes logger mode, health status, selected tool function, user/share/session/RPC/IPC/SPNEGO/worker subsystems, and config-derived globals. `set_conf_contents` writes configuration files with owner/group-limited mode.

## Dependencies and Integration Points

It links every major ksmbd-tools subsystem and the command-specific `*_main` functions. It depends heavily on GLib helpers through `tools.h` and config/management modules.

## Risks and Edge Cases

`base64_decode` writes a trailing NUL at `ret[*dstlen]`, assuming GLib provides enough room. `ksmbd_gconvert` retries UTF-16/UCS-2 aliases but returns NULL after logging conversion errors. Startup ordering is significant: SPNEGO sees parsed global Kerberos config, and worker pool starts after IPC/RPC initialization.

## Test Signals

Test basename dispatch, each tool mode's config lifecycle, syslog/stdout logging, charset conversion fallback, config file creation permissions, mountd init/teardown order, and version output.
