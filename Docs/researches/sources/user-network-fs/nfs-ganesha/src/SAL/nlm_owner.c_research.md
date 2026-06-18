# sources/user-network-fs/nfs-ganesha/src/SAL/nlm_owner.c

Purpose: Implements NSM client, NLM client, and NLM lock-owner caches used by Network Lock Manager state, including monitor integration, RPC callback client lifetime, and owner lookup/deduplication.

Important APIs, types, and functions: Global tables are `ht_nsm_client`, `ht_nlm_client`, and `ht_nlm_owner`. Key functions include `Init_nlm_hash`, `get_nsm_client`, `inc_nsm_client_ref`, `dec_nsm_client_ref`, `get_nlm_client`, `inc_nlm_client_ref`, `dec_nlm_client_ref`, `get_nlm_owner`, and the compare/hash/display helpers for `state_nsm_client_t`, `state_nlm_client_t`, and `state_owner_t` NLM owners.

Control flow: NSM lookup builds a caller-name key either from the protocol caller name or canonicalized caller address, then deduplicates through `ht_nsm_client`; `CARE_MONITOR` starts NSM monitoring before returning. NLM client lookup keys on NSM client, local server address from `getsockname`, transport type, and NLM caller name; it refs the NSM client and can also monitor. NLM owners key on NLM client, svid, and opaque owner handle, then delegate allocation to the generic `get_state_owner` cache with `init_nlm_owner`. Refcount zero paths remove the object from its hash table under a latch and tolerate already-removed or replaced entries.

State and persistence behavior: All owner/client state is in-memory. NSM monitoring is external process/protocol state managed through `nsm_monitor` and `nsm_unmonitor`. NLM clients may own libtirpc callback `CLIENT` handles; TCP callbacks are configured with `CLSET_FD_CLOSE` before `CLNT_DESTROY` to close sockets. There is no direct durable persistence.

Dependencies and integration points: Integrates with `op_ctx->client`, caller addresses, NSM monitor code, libtirpc transports, Ganesha client manager refs, generic state-owner cache, hash latches, and `nfs_param.core_param.nsm_use_caller_name`. NLM recovery release in `nfs4_recovery.c` walks `ht_nlm_client`.

Risks: The NSM key intentionally ignores `ssc_client` and compares only caller name/address, which is required for SM_NOTIFY but can merge clients if caller names are ambiguous. Hash functions are simple byte sums and rely on compare for correctness. `get_nlm_client` assumes `xprt->xp_fd` and `getsockname` are usable; missing local address reduces key quality. Monitor failure must unwind references and likely remove just-created hash entries. Refcount-zero deletion races are expected and handled, but missed refs can leak monitors or callback sockets.

Test signals: Cover caller-name versus address-based NSM keys, SM_NOTIFY-style lookup with no `op_ctx->client`, monitor success/failure unwinding, NLM client keys across transport/local address/caller name, callback client destruction, owner dedup by svid and netobj, and concurrent lookup versus final ref release.
