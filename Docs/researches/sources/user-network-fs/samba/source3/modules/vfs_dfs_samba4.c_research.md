# sources/user-network-fs/samba/source3/modules/vfs_dfs_samba4.c

## Purpose
`vfs_dfs_samba4.c` retrieves DFS referrals from Samba AD/SAMDB using Samba4 libraries and falls back to lower VFS referral logic when AD reports not found.

## Important APIs, Types, And Functions
`struct dfs_samba4_handle_data` stores event, loadparm, and SAMDB contexts. `dfs_samba4_connect()` initializes those contexts after lower connect. `dfs_samba4_get_referrals()` calls `dfs_server_ad_get_referrals()` with the remote client address. The module registers connect, disconnect, and get-referrals hooks.

## Control Flow
Connect is all-or-fail: allocation, event context, loadparm, or samdb failures call lower disconnect and return `-1`. Referral lookup uses handle data, delegates to AD DFS lookup, falls back only on `NT_STATUS_NOT_FOUND`, and returns all other errors directly.

## State And Persistence
Per-connection handle data is talloc-owned. Persistent DFS data lives in AD/SAMDB. A custom debug class is registered at init.

## Dependencies And Integration Points
The module bridges source3 VFS with source4 event, loadparm, auth/session, SAMDB, and DFS server AD helpers.

## Risks
SAMDB availability is mandatory for AD lookups. Only not-found falls back, so transient AD errors reach clients. Failure cleanup relies on lower disconnect and talloc ownership. A debug message labels the class as `fileid`, likely cosmetic.

## Test Signals
Test successful AD referrals, not-found fallback, initialization failures, remote address handling, disconnect cleanup, and debug class registration.
