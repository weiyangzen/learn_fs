# sources/user-network-fs/samba/source3/utils/smbpasswd.c

## Purpose

`sources/user-network-fs/samba/source3/utils/smbpasswd.c` implements the `smbpasswd` command-line tool. It changes SMB passwords locally through Samba passdb, remotely through password-change RPC, and, for root, performs administrative account operations such as add/delete/enable/disable users, machine or interdomain trust accounts, no-password state, and storing the LDAP admin password in `secrets.tdb`. The source was read as a complete 678-line file.

## Important APIs, Types, and Functions

Important entry points are `main`, `process_options`, `process_root`, `process_nonroot`, `password_change`, `prompt_for_new_password`, `store_ldap_admin_pw`, and `usage`. Global state includes `got_username`, `stdin_passwd_get`, `user_name`, `new_passwd`, `remote_machine`, and `ldap_secret`. The code uses local operation flags from `passwd_proto.h` such as `LOCAL_AM_ROOT`, `LOCAL_SET_PASSWORD`, `LOCAL_ADD_USER`, `LOCAL_DELETE_USER`, `LOCAL_DISABLE_USER`, `LOCAL_ENABLE_USER`, `LOCAL_TRUST_ACCOUNT`, `LOCAL_INTERDOM_ACCOUNT`, `LOCAL_SET_NO_PASSWORD`, and `LOCAL_SET_LDAP_ADMIN_PW`.

## Control Flow

`main` initializes memcache, locale, loadparm, and command-line parsing, rejects setuid-root execution, then dispatches to `process_root` when uid 0 or `process_nonroot` otherwise. `process_options` handles legacy getopt flags, loads the selected `smb.conf`, and sets local operation flags. Root mode initializes secrets/passdb, normalizes trust account names with a trailing `$`, prompts for generated or explicit passwords as needed, and calls `password_change`. Non-root mode restricts flags to password changes, infers the local username, allows `DOMAIN\user` parsing, uses localhost when no remote host is specified, prompts for old and new passwords, and performs a remote password change.

## State and Persistence Behavior

Local password changes mutate the configured passdb backend through `local_password_change`. Remote changes are sent to the target machine with `remote_password_change`. `-w` and `-W` store LDAP admin credentials in `secrets.tdb` via `secrets_store_ldap_pw`. The tool holds plaintext passwords in heap/fstring buffers only for the command lifetime and frees many of them on exit, but the source does not explicitly scrub every heap allocation after use.

## Dependencies and Integration Points

The utility integrates with Samba loadparm, passdb, secrets, local password utilities, remote password-change helpers, name resolution ordering, interface loading, and command-line contexts. It depends on `get_pass`, Unix passwd lookup, `initialize_password_db`, `get_global_sam_sid`, and `samba_cmdline`/loadparm helpers.

## Risks and Edge Cases

Option parsing is old-style and stateful; combinations such as local add/delete with remote operations are rejected only after parsing. Root-only operations are sensitive because they can change passdb entries or store LDAP secrets. Trust account name manipulation must avoid overflowing the fixed `fstring`. Non-root changes always go through a remote path, including localhost, so network/service availability affects local user workflows. Password handling is security-sensitive because values pass through process memory and optional stdin mode.

## Test Signals

Useful tests include CLI option matrix coverage, setuid-root rejection, root versus non-root flows, local passdb add/delete/enable/disable/no-password operations, remote password-change failures, trust-account `$` normalization, LDAP admin password storage with and without stdin prompting, and valgrind/sanitizer checks for prompt and error paths.
