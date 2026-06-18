# sources/user-network-fs/ksmbd-tools/tools/config_parser.c

## Purpose

`config_parser.c` parses ksmbd configuration files and turns text configuration into process-local global config, users, shares, generated SID subauthority values, and daemon lock state. It handles Samba-like `smb.conf` groups/key-values, the ksmbd password database, subauth and lock files, and externally supplied addshare options. The source was read as a complete 1011-line file.

## Important APIs, Types, and Functions

Public parser helpers include `cp_parse_smbconf`, `cp_parse_pwddb`, `cp_parse_subauth`, `cp_parse_lock`, `cp_parse_external_smbconf_group`, `cp_smbconf_parser_init`, `cp_smbconf_parser_destroy`, `cp_memparse`, `cp_get_group_kv_*`, `cp_group_kv_steal`, `cp_ltrim`, `cp_rtrim`, and `cp_key_cmp`. Global variables are `global_conf` and `parser`. Major internals validate groups and key-values, mmap files line by line, apply global defaults, propagate global share defaults, and process user/password/subauth/lock records.

## Control Flow

`__mmap_parse_file` opens a file, maps it, splits it into lines, and calls a file-specific `process_entry` function. `cp_parse_smbconf` accumulates groups, recursively validates nested parser ownership when needed, then `finalize_smbconf_parser` injects `[global]` and `[ipc$]` defaults, processes global options, copies global share options into all shares, creates shares through `shm_add_new_share`, logs ignored keys, and destroys parser state. Password parsing validates `name:base64hash`, updating or creating users. Subauth and lock parsing either read existing state or create mountd-owned defaults.

## State and Persistence Behavior

Parsed state persists in `global_conf`, the user manager, and the share manager. `set_conf_contents` can create missing config, password database, subauth, and lock files with restricted permissions. On reload, `KSMBD_SHOULD_RELOAD_CONFIG` changes stealing behavior so existing config values can be refreshed without resetting defaults in the same way as startup.

## Dependencies and Integration Points

It depends on GLib mapped files/hash tables, POSIX file APIs, `linux/ksmbd_server.h`, `management/user.h`, and `management/share.h`. It is called by `tools.c` during `load_config` for all ksmbd tool modes.

## Risks and Edge Cases

`cp_key_cmp` compares only the length of the right-hand key, so callers rely on canonical lookup strings to avoid prefix ambiguity. `cp_memparse` shifts without overflow checks. Lock handling trusts `kill(pid, 0)` and can be affected by permissions. File parsing stops after the first valid subauth/lock entry. Defaults and reload behavior are subtle because key stealing mutates group hash tables.

## Test Signals

High-value tests parse representative smb.conf files, duplicate keys, invalid UTF-8 names/comments, missing files in each tool mode, reload behavior, global-to-share default propagation, lock/subauth creation, base64 password validation, and boundary values for `max connections`, `sessions_cap`, and size suffix parsing.
