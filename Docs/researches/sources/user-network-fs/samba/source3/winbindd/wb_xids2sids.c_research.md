# sources/user-network-fs/samba/source3/winbindd/wb_xids2sids.c

Purpose: maps an ordered list of Unix IDs to SIDs by consulting idmap cache and then iterating configured idmap domains.

Important APIs and types: `wb_xids2sids_send/recv`; top-level `struct wb_xids2sids_state`; per-domain `struct wb_xids2sids_dom_state`; helper `wb_xids2sids_dom_send/recv`; callbacks `wb_xids2sids_idmap_setup_done`, `wb_xids2sids_done`, `wb_xids2sids_dom_done`, and `wb_xids2sids_dom_gotdc`.

Control flow: `send` copies input XIDs, initializes null SIDs and cached flags, and pre-fills nonexpired cache hits via `idmap_cache_find_xid2sid`. It loads idmap config, then dispatches `wb_xids2sids_dom_send` for each configured domain in order. Each domain filters XIDs by configured range, cache status, and already-filled SID, then calls `dcerpc_wbint_UnixIDs2Sids_send`. Domain-controller-not-found/host-unreachable can trigger DC rediscovery and retry. After all domains, uncached results are written back to the SID-to-Unix cache with backend-returned XID type values. `recv` moves the SID array to the caller.

State and persistence: request-local state plus idmap cache reads/writes, failed connection markers, and DC discovery gencache updates.

Dependencies and integration points: idmap child RPC, parent idmap config/ranges, cache helpers, DC discovery, netlogon types, and public `XIDS_TO_SIDS` winbind command handling.

Risks: configured domain ordering determines which range match wins. Null SIDs represent unresolved entries and are still cached at the end unless guarded by idmap cache semantics. Backend may adjust XID type; cache priming intentionally uses returned type rather than requested type. Count alignment in per-domain responses relies on iterating the same filtered XID set in the callback.

Test signals: cache hit, expired/missing cache, XIDs outside every domain range, overlapping ranges, backend returns none mapped, host-unreachable/DC retry, returned type changes, and preservation of input ordering with mixed cached and uncached IDs.
