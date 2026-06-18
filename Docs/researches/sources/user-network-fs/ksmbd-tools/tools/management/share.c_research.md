# sources/user-network-fs/ksmbd-tools/tools/management/share.c

## Purpose

`share.c` implements ksmbd share management. It validates and stores share definitions parsed from smb.conf, maintains a ref-counted global share table, expands user/group and host access maps, applies share flags and masks, tracks connection counts, and serializes share configuration into kernel IPC responses. The source was read as a complete 961-line file.

## Important APIs, Types, and Functions

Public APIs include `shm_init`, `shm_destroy`, `shm_add_new_share`, `shm_lookup_share`, `get_ksmbd_share`, `put_ksmbd_share`, `shm_remove_all_shares`, `shm_lookup_users_map`, `shm_lookup_hosts_map`, `shm_open_connection`, `shm_close_connection`, `shm_iter_shares`, `shm_share_config_payload_size`, `shm_handle_share_config_request`, `shm_share_name`, `shm_share_name_hash`, `shm_share_name_equal`, and `shm_share_config`. Key static routines parse individual share options through `process_share_conf_kv`.

## Control Flow

Config finalization creates a `ksmbd_share`, initializes defaults, marks reload updates when needed, and processes group key-values into fields and flags. Share table insertion rejects casefolded duplicate names. Tree connect looks up a share, increments connection count through `shm_open_connection`, checks host/user maps, and later uses `shm_handle_share_config_request` to build the kernel-facing response payload.

## State and Persistence Behavior

Share state is process-local in `shares_table`, protected by `shares_table_lock`, and each share has update/maps locks and a refcount. Maps hold borrowed or referenced `ksmbd_user` objects. Persistence originates from smb.conf, but this file itself does not write disk state.

## Dependencies and Integration Points

It depends on GLib hash/UTF-8/casefold helpers, POSIX passwd/group APIs, `config_parser.h`, `management/user.h`, and `linux/ksmbd_server.h`. It feeds tree connection authorization and share config IPC responses.

## Risks and Edge Cases

`shm_open_connection` increments before checking `>= max_connections`, and error paths in tree connection also close the share, so off-by-one and double-close behavior need coverage. Host allow/deny maps are exact strings with a FIXME for real IP/mask matching. Group expansion scans system passwd/group databases at parse time. Veto-list parsing assumes a leading delimiter and rewrites slashes to NULs.

## Test Signals

Tests should cover UTF-8/casefold share names, duplicate shares, every share option, group expansion, guest account creation, host allow/deny semantics, max-connection boundaries, IPC payload sizing with root dir and veto lists, and reload update flags.
