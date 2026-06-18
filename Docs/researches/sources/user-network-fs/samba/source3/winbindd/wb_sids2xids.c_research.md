# sources/user-network-fs/samba/source3/winbindd/wb_sids2xids.c

Purpose: maps an ordered list of SIDs to Unix IDs, using idmap cache first, idmap backend calls by domain next, and SID name lookup to obtain type hints when the backend requests them.

Important APIs and types: `wb_sids2xids_send/recv`; `struct wb_sids2xids_state`; `wbint_TransIDArray`; `wb_parent_idmap_config`; helper `wb_sids2xids_in_cache`; callback sequence `idmap_setup_done`, `next_sids2unix`, `done`, `lookupsids_done`, and `gotdc`; `lsa_SidType_to_id_type`.

Control flow: `send` copies SIDs, initializes invalid `all_ids` entries, splits RIDs, and fills cache hits with `idmap_cache_find_sid2unixid`. If unresolved entries remain it loads parent idmap config. The setup callback builds `idmap_doms` for unresolved SIDs, using configured domains, known domains, predefined SID type hints, and default hints. `next_sids2unix` batches unresolved IDs by domain and calls `dcerpc_wbint_Sids2UnixIDs_send` on the idmap child. If the backend returns `ID_TYPE_WB_REQUIRE_TYPE`, the code batches remaining SIDs through `wb_lookupsids_send`, derives type hints, and restarts idmap mapping. Domain-controller-not-found/host-unreachable can trigger `wb_dsgetdcname_send` and a retry. `recv` copies final `unixid` values into the caller's output array.

State and persistence: reads and writes idmap cache entries with `idmap_cache_set_sid2unixid`, including negative/not-specified results. Uses gencache for DC discovery via `wb_dsgetdcname_gencache_set` and failed-connection tracking via `winbind_idmap_add_failed_connection_entry`.

Dependencies and integration points: idmap child RPC, parent idmap config, domain list, predefined SID lookup, `wb_lookupsids.c`, netlogon DC discovery, LSA domain lists, and higher-level `SIDS_TO_XIDS` winbind commands.

Risks: negative cache insertion affects later calls; expired cache is ignored only when the own domain is online. Correct `tmp_idx` maintenance is essential for preserving input order after per-domain batches. Backend responses with mismatched counts are fatal. Type-hint retry loops must avoid exposing `ID_TYPE_WB_REQUIRE_TYPE` outside winbindd. DC rediscovery is single-shot per domain.

Test signals: all-cache-hit path, expired cache online/offline behavior, configured-domain match, unknown-domain fallback, predefined SID type hint, backend requiring type hints, none-mapped negative cache, count mismatch, host-unreachable/DC rediscovery retry, and output order preservation.
