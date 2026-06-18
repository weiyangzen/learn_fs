# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/ridalloc.c

## Purpose
`ridalloc.c` implements helper routines for RID Set and RID Manager handling in the Samba AD DC. It allocates individual RIDs from the local DC's RID Set, creates RID Set objects when needed, obtains fresh RID pools from the RID Manager FSMO, and services the DRS extended operation used by a RID Manager to allocate pools for another DC.

## Important APIs, Types, And Functions
`struct ridalloc_ridset_values` is the local normalized form of `rIDAllocationPool`, `rIDPreviousAllocationPool`, `rIDNextRID`, and `rIDUsedPool`. `ridalloc_get_ridset_values()` reads those fields from an LDB message, while `ridalloc_set_ridset_values()` emits constrained updates with `dsdb_msg_constrainted_update_uint64()` and `dsdb_msg_constrainted_update_uint32()`, omitting unchanged or absent sentinel values.

`ridalloc_poke_rid_manager()` sends `MSG_DREPL_ALLOCATE_RID` to the local `dreplsrv` service so replication can ask the remote RID Manager for a new pool asynchronously. `ridalloc_rid_manager_allocate()` consumes 500 RIDs from `rIDAvailablePool` on the RID Manager object using a constrained update. `ridalloc_create_rid_set_ntds()` creates a `CN=RID Set` child under a DC machine account and links it through `rIDSetReferences`. Public helpers include `ridalloc_create_own_rid_set()`, `ridalloc_new_own_pool()`, `ridalloc_allocate_rid()`, and `ridalloc_allocate_rid_pool_fsmo()`.

## Control Flow
Individual RID allocation starts in `ridalloc_allocate_rid()`. It locates this DC's RID Set with `samdb_rid_set_dn()` and creates it if the reference is missing. It reads the current RID Set values, initializes `rIDPreviousAllocationPool` and `rIDNextRID` on first use, increments `rIDNextRID` on subsequent use, and switches to `rIDAllocationPool` when the previous pool is exhausted. If no standby pool is available, it calls `ridalloc_new_own_pool()`; that routine either updates locally when this DC owns the RID Manager FSMO or pokes `dreplsrv` and returns `LDB_ERR_UNWILLING_TO_PERFORM`.

When the active pool is more than half exhausted and no standby pool exists, `ridalloc_allocate_rid()` proactively tries to obtain a standby pool. A remote-manager `LDB_ERR_UNWILLING_TO_PERFORM` is treated as non-fatal in this early-refresh case because the asynchronous poke has been sent. The final RID Set update is a constrained modify as system, which protects against lost updates if another allocator changed the same values.

`ridalloc_allocate_rid_pool_fsmo()` is the remote-allocation path called by the DRS `DSDB_EXTENDED_ALLOCATE_RID_POOL` operation. It resolves the destination DSA GUID to an NTDS object, finds the server's machine account, creates the RID Set if missing, validates optional `fsmo_info` against the current allocation pool for idempotence, takes a new pool from the RID Manager, and writes it into the remote DC's RID Set.

## State And Persistence
Persistent state lives in directory objects: the RID Manager's `rIDAvailablePool`, each DC machine account's `rIDSetReferences`, and each RID Set's allocation fields. The file itself stores no durable process state. Messaging to `dreplsrv` is asynchronous and advisory; the database changes are made through LDB constrained updates and `DSDB_FLAG_AS_SYSTEM` where ownership or security descriptors matter.

## Dependencies And Integration Points
The code depends on DSDB module helper APIs, Samba messaging and IRPC (`imessaging_client_init()`, `irpc_servers_byname()`, `imessaging_send()`), loadparm context, GUID/NTDS helpers, RID Manager DN helpers, and DRS FSMO extended-operation types. It integrates with `samldb` for object creation that needs RIDs, with replication for remote pool requests, and with the RID Manager FSMO ownership model.

## Risks And Test Signals
RID allocation correctness depends on constrained updates and retry behavior in callers; this file returns conflicts/errors but does not loop internally. `ridalloc_rid_manager_allocate()` allocates fixed 500-RID pools and must correctly pack low/high 32-bit halves. Edge cases include exhausted `rIDAvailablePool`, missing `serverReference`, missing or corrupt RID Set attributes, stale NTDS GUID cache, remote RID Manager unavailability, and idempotent DRS retries with `fsmo_info`. Tests should simulate first RID allocation, pool rollover, half-pool refresh, local versus remote FSMO behavior, RID Set creation security, `rIDAvailablePool` exhaustion, constrained-update conflicts, and DRS remote allocation for both new and existing RID Sets.
