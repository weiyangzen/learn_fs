# sources/user-network-fs/ksmbd-tools/tools/management/user.c

## Purpose

`user.c` manages ksmbd user records loaded from the password database and synthesized guest accounts. It stores decoded password hashes, uid/gid/supplementary groups, login flags, failed-login state, and ref-counted lifetime. The source was read as a complete 471-line file.

## Important APIs, Types, and Functions

Public APIs include `usm_init`, `usm_destroy`, `usm_add_new_user`, `usm_add_guest_account`, `usm_lookup_user`, `get_ksmbd_user`, `put_ksmbd_user`, `usm_remove_user`, `usm_remove_all_users`, `usm_update_user_password`, `usm_user_name`, `usm_iter_users`, `usm_handle_login_request`, `usm_handle_login_request_ext`, and `usm_handle_logout_request`.

## Control Flow

Password parsing calls `usm_add_new_user` or `usm_update_user_password`. New user creation resolves uid/gid with `getpwnam`, decodes the base64 password hash, and collects supplementary groups with `getgrouplist`. Login lookup returns the hash, account, uid/gid, flags, and extension marker when groups exist; null or bad-user login may map to the configured guest account. Extended login responses copy supplementary group IDs into the variable payload.

## State and Persistence Behavior

User state is in-memory in `users_table`, protected by `users_table_lock`; each user has an update lock and refcount. Persistent source state is the password database and system passwd/group databases. Failed login count and delayed-session flag persist only for the process lifetime.

## Dependencies and Integration Points

It depends on GLib, POSIX group/passwd APIs, `config_parser.h`, share constants, and kernel IPC structs. The worker login path and tree connection authorization depend on this module.

## Risks and Edge Cases

`base64_decode` appends a NUL byte after GLib allocation assumptions; malformed password text should be tested. Users missing from `/etc/passwd` are accepted with invalid uid/gid, which may be intentional but affects authorization. `usm_handle_login_request_ext` copies group payload based on prior sizing assumptions. Failed-login counters are modified without the user's update lock.

## Test Signals

Cover valid users, duplicate users, password updates, missing system accounts, supplementary group payloads, guest mapping, null sessions, failed-password delay thresholds, UTF-8/colon username validation, and concurrent lookup/remove.
