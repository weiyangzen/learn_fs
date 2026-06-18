# sources/object-store/daos/src/vos/vos_ts.h

Purpose: declares timestamp-cache structures and inlines for VOS transactional conflict tracking across container, object, dkey, and akey hierarchy levels.

Important APIs/types: defines `vos_ts_info`, `vos_ts_pair`, `vos_wts_cache`, `vos_ts_entry`, `vos_ts_set_entry`, `vos_ts_set`, `vos_ts_table`, read/write flag bits, and timestamp type counts. Inline helpers include `vos_ts_in_tx`, lookup/allocation helpers, `vos_ts_get_negative`, `vos_ts_wcheck`, `vos_ts_set_add`, `vos_ts_set_mark_entry`, `vos_ts_evict`, `vos_ts_peek_entry`, `vos_ts_set_check_conflict`, `vos_ts_set_update`, `vos_ts_set_wupdate`, and state save/restore.

Control flow and state: callers allocate a `vos_ts_set`, add entries as VOS descends through object/dkey/akey records, optionally use negative entries for missing subtrees, then update read or write timestamps after operation success. The table keeps high/low read timestamps and the two highest write timestamps needed for uncertainty-bound checks. `vos_ts_set_add` advances expected hierarchy type automatically, hashes object IDs specially, and uses TLS saved hashes for keys.

Dependencies/integration: includes DAOS DTX types, VOS TLS, and `lru_array`. It is designed for hot-path inlining and is used by tree and ilog code to coordinate conditional fetch/update semantics with DTX conflict checks.

Risks: many functions are no-ops when not in a real transaction, so caller flag correctness is essential. `ts_set_size` must account for all akeys or `-DER_BUSY` can occur. `vos_ts_set_get_entry_type` computes indexes from type/akey index and relies on ordering assumptions. `vos_ts_wcheck` is conservative when the write cache lacks enough history, which can reject operations under uncertainty.

Test signals: cover hierarchy insertion order, duplicate or repeated akey handling, negative lookup paths, hash-index derivation from parent entries, write uncertainty cases documented in `vos_ts_wcheck`, read/write level selection, and save/restore around speculative tree probes.
