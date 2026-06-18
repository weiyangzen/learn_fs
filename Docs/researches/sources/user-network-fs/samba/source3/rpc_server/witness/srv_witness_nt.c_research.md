# sources/user-network-fs/samba/source3/rpc_server/witness/srv_witness_nt.c

## Purpose
`srv_witness_nt.c` implements Samba's server-side Witness RPC endpoint for Scale-Out File Server style notifications in CTDB clusters. It answers interface-list queries, accepts Witness v1/v2 registrations, persists registration metadata for other rpcd components, tracks CTDB IP ownership changes, and completes asynchronous `AsyncNotify` calls when resource, client-move, share-move, or forced responses are triggered.

## Important APIs, types, and functions
- `struct swn_service_globals` is the process-global Witness service state: DCE context, connection registration DB, server name, local CTDB VNN, cached interface list generation, registration list, and persistent registration TDB.
- `struct swn_service_interface` represents one advertised IPv4/IPv6 interface with group name, state, local/nonlocal flag, current VNN, and generation counters.
- `struct swn_service_registration` owns the policy handle, client/net/share identity, registered IP, queued notifications, usage expiry timer, forced unregister timer, messaging listener, and async notify queue.
- `swn_service_init_globals()` opens the in-memory connection DB and `rpcd_witness_registration.tdb` with mode `0600`, initializes CTDB callbacks, and installs the global destructor.
- `swn_service_reload_interfaces()` refreshes CTDB public/node IP state through `ctdbd_all_ip_foreach()` and marks disappeared interfaces unavailable before deleting them.
- `_witness_GetInterfaceList()`, `_witness_Register()`, `_witness_RegisterEx()`, `_witness_UnRegister()`, and `_witness_AsyncNotify()` are the exported RPC operations.
- `swn_server_registration_message_done()` consumes `MSG_RPCD_WITNESS_REGISTRATION_UPDATE` messages and converts rpcd-internal registration updates into queued Witness notifications.

## Control flow
Startup is lazy: bind, register, or interface-list calls invoke global initialization and interface reload. Interface reload increments a generation, reads CTDB IP assignments, filters loopback and link-local addresses, adds or updates interfaces, and notifies matching registrations when state, owner VNN, or local-interface status changes. CTDB `IPREALLOCATED` callbacks invalidate the cache and force a reload.

Registration validates protocol version, required strings, server net name, and numeric IP address. v2 additionally sanity-checks share name by requiring log escaping to preserve the string. After matching the IP to a known interface, registration creation allocates state, creates a policy handle, starts a filtered messaging read, creates a stopped async queue, installs expiry timers, links into memory, and stores an NDR-encoded `rpcd_witness_registration` keyed by policy-handle GUID.

Async notification calls look up the policy handle, update usage, mark the DCERPC call asynchronous, and wait on the registration queue. Triggers are prioritized: forced responses, resource changes, client moves, share moves, and currently unimplemented IP notifications. Some unavailable or moved-away cases schedule a five-second forced unregister so Windows clients re-register cleanly.

## State and persistence behavior
Runtime state is held under `swn_globals` and talloc-owned registration/interface lists. Persistent cross-process state is the lock-path `rpcd_witness_registration.tdb`, which contains sensitive client keys, account names, SIDs, endpoints, registration time, context handles, and requested registration parameters. Registration destruction stops the async queue, completes outstanding waiters with not-found behavior, deletes the TDB row, unlinks from the global list, and drops the policy handle.

## Dependencies and integration points
This file integrates with CTDB, Samba messaging, dbwrap/TDB, talloc, tevent queues/timers, DCE/RPC server internals, generated Witness and rpcd-witness NDR, policy handles, Samba address utilities, and loadparm configuration. It is enabled only when CTDB support is available through the build file's `RPC_WITNESS` and `rpcd_witness` definitions.

## Risks and edge cases
- Async lifetime crosses policy handles, talloc destructors, tevent queues, CTDB callbacks, and DCE/RPC orphan/cancel paths.
- `rpcd_witness_registration.tdb` contains sensitive data and must remain private and reliably cleaned.
- Interface changes deliberately emit transient unavailable states when VNN or locality changes.
- `swn_service_async_notify_send()` has a missing semicolon after `tevent_queue_add_entry(...)` in the inspected source, a direct compile-break signal if this exact tree is built.
- The five-second forced unregister workaround is tuned for observed Windows Server behavior and may be client-version sensitive.

## Test signals
Useful validation includes CTDB-enabled builds, Witness bind authentication levels, interface listing, v1/v2 register/unregister, orphaned/cancelled `AsyncNotify`, CTDB IP failover/reallocation, rpcd registration update messages, and checks that TDB rows are inserted and deleted.
