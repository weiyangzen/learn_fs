<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/addshare/addshare.c -->
# sources/user-network-fs/ksmbd-tools/addshare/addshare.c

## Purpose

CLI front end for `ksmbd.addshare`. It parses command options, validates a share name, loads current configuration, dispatches add/update/delete behavior, and notifies mountd after successful changes.

## Important APIs, Types, and Functions

Important APIs are `addshare_main`, `usage`, getopt option descriptors, `command_add_share`, `command_update_share`, `command_delete_share`, `load_config`, `cp_parse_lock`, and `kill(..., SIGHUP)`. It uses GLib automatic cleanup and `gptrarray_to_strv` for repeated `-o` options.

## Control Flow

The command loop records a requested operation and option strings, requires exactly one SHARE argument, validates it with `shm_share_name`, defaults paths to `PATH_PWDDB` and `PATH_SMBCONF`, loads users and shares, auto-selects add versus update when no operation is supplied, then calls the selected share-admin command.

## State and Persistence Behavior

Persistent state is the rewritten `ksmbd.conf` performed by share_admin.c. After a successful command it reads the lock file to find mountd and sends SIGHUP unless the lock cannot be parsed.

## Dependencies and Integration Points

Depends on config parsing, tools helpers, management share/user state, kernel share name limits from `ksmbd_server.h`, and the share_admin command contract.

## Risks and Edge Cases

Multiple `-a/-u/-d` flags overwrite the selected command instead of being rejected. SIGHUP failure does not convert a successful config write into a failed exit. The loaded parser state must be removed on every exit path.

## Test Signals

Test with add, update, delete, auto add/update, invalid UTF-8 or too-long names, repeated options, custom config/password paths, absent lock file, and live mountd reload notification.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/addshare/addshare.c -->
