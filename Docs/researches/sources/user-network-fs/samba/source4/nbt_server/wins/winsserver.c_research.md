# sources/user-network-fs/samba/source4/nbt_server/wins/winsserver.c

## Purpose

`winsserver.c` implements the core WINS server request path for NetBIOS name registration, refresh, query, release, WACK conflict challenges, and server startup. It translates NBT packets into WINS DB operations and Windows-compatible registration/query/release behavior.

## Important APIs, Types, and Functions

Public entry points are `wins_server_ttl()`, `nbtd_winsserver_request()`, and `nbtd_winsserver_init()`. Key helpers include `wrepl_type()`, `wins_register_new()`, `wins_update_ttl()`, `wins_sgroup_merge()`, `wins_register_wack()`, `wins_wack_allow()`, `wins_wack_deny()`, `wack_wins_challenge_handler()`, `nbtd_winsserver_register()`, `nbtd_winsserver_query()`, `nbtd_winsserver_release()`, and `nbtd_wins_randomize1Clist()`.

## Control Flow

Request dispatch ignores broadcasts and disabled WINS state, then handles query, register/refresh/multihome-register, and release opcodes. Registration validates special NetBIOS names, checks duplicate WACKs, looks up existing records, creates new records, refreshes TTLs, merges special groups, rejects incompatible static or group records, or starts WACK challenges for conflicting unique/multihomed owners. Query rejects master-browser 0x1D, optionally prepends 0x1B to 0x1C results, returns group wildcard addresses, randomizes 0x1C lists when configured, falls back to DNS proxy for eligible misses, and sends positive or negative replies. Release verifies ownership by source address, mutates active/released/tombstone state, updates expiration and ownership for replication cases, and always sends a positive release reply to match Windows behavior.

## State and Persistence Behavior

Persistent state is in `wins.ldb` via `winsdb_add()`, `winsdb_modify()`, and `winsdb_delete()`. In-memory WACK state is linked on `iface->wack_queue` and removed by destructor. Startup stores WINS configuration intervals and a connected `winsdb_handle` in `nbtsrv->winssrv`, choosing the local owner from `winsdb:local_owner` or the first IPv4 interface.

## Dependencies and Integration Points

It depends on nbtd packet/socket helpers, WINS DB APIs, WACK helper `wins_challenge_send()`, LDB, loadparm, interface utilities, resolver/DNS proxy, talloc list helpers, and generated NBT/WREPL constants. It registers the IRPC name `wins_server` at initialization and is built into the `NBTD_WINS` subsystem.

## Risks and Edge Cases

The registration branch contains a duplicated `new_type == WREPL_TYPE_GROUP` condition where the second check likely intended `SGROUP`. `nbtd_winsserver_init()` reads `" tombstone_timeout"` with a leading space in the parameter name, which may prevent intended config override. WACK allow deletes and re-adds records if the old owner no longer holds the name; races are guarded by version/owner re-lookup but remain subtle. Release only checks source address, with a TODO about packet additional address verification. Address iteration while removing entries must be handled carefully.

## Test Signals

Tests should cover name-type validation for 0x1B/0x1C/0x1D/0x1E, static record handling, unique conflicts and WACK allow/deny, duplicate WACK suppression, multihomed and special group registration, TTL clamping, query group and 1C behavior, DNS proxy fallback, release from owner versus non-owner, tombstone ownership transitions, and startup with/without WINS enabled.
