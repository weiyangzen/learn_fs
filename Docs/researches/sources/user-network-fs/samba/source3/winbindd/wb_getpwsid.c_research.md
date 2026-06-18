# sources/user-network-fs/samba/source3/winbindd/wb_getpwsid.c

## Purpose
This async helper fills a `struct winbindd_pw` passwd-style record for a user SID. It queries user information, normalizes mapped names through the idmap child, and applies Samba substitution rules to home directory and shell.

## Important APIs, Types, And Functions
`struct wb_getpwsid_state` stores SID, userinfo, output `winbindd_pw`, and normalized name. Public APIs are `wb_getpwsid_send` and `wb_getpwsid_recv`. Callbacks are `wb_getpwsid_queryuser_done` and `wb_getpwsid_normalize_done`.

## Control Flow
The send function rejects unmapped Unix user SIDs and calls `wb_queryuser_send`. The query callback lowercases the account name, then sends `dcerpc_wbint_NormalizeNameMap` to the idmap child. The normalize callback accepts OK and `NT_STATUS_FILE_RENAMED` as mapped-name results, builds a domain-qualified output username, copies UID/GID/full name, substitutes variables in homedir and shell with `talloc_sub_specified`, sets password to `*`, and completes.

## State And Persistence
Only request-local state is used. Normalization may depend on idmap child/backend config, but this helper writes no persistent data.

## Dependencies And Integration
It depends on `wb_queryuser`, generated winbind RPC stubs, idmap child handle, username formatting, string wrappers, and substitution helpers. It feeds winbind NSS passwd responses.

## Risks And Test Signals
Test Unix user SID rejection, queryuser failures, lowercase normalization, name-map OK/renamed/failure results, long field truncation in fixed-size passwd buffers, null full name, homedir/shell substitution, and memory ownership of moved strings.
