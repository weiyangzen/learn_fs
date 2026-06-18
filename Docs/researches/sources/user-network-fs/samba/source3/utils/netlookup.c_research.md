# sources/user-network-fs/samba/source3/utils/netlookup.c

## Purpose
Provides local LSA helper lookups between names and SIDs, mainly for usershare ACL conversion and display.

## Important APIs, Types, and Functions
`struct con_struct` caches failed connection state, `cli_state`, LSA pipe, and policy handle. `create_cs()` connects anonymously to local `IPC$`, opens LSA, and opens a policy handle. `net_lookup_name_from_sid()` calls `rpccli_lsa_lookup_sids()`. `net_lookup_sid_from_name()` calls `rpccli_lsa_lookup_names()`. `cs_destructor()` shuts down the cached connection.

## Control Flow
Lookup functions call `create_cs()`. Existing successful cache is reused; existing failed cache returns the stored error. New setup initializes anonymous credentials, connects to `127.0.0.1`, opens the pipe/policy, then performs one lookup.

## State and Persistence
Only process-local static cache state is held. No persistent files are written.

## Dependencies and Integration Points
Depends on libsmb connection, anonymous credentials, local NetBIOS/loadparm settings, LSA RPC helpers, and local smbd/winbind name resolution.

## Risks
The static cache is not thread-safe and caches failures until destruction. Local anonymous LSA access must be available. Destructor uses global `cs`, making cache assumptions important.

## Test Signals
Cover successful name/SID conversions, smbd unavailable, pipe/policy failures, cached failure behavior, destructor cleanup, anonymous credential allocation failure, and usershare ACL integration.
