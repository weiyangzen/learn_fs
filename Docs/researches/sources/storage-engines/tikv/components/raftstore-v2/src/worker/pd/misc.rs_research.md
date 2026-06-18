# sources/storage-engines/tikv/components/raftstore-v2/src/worker/pd/misc.rs

Purpose: this file contains miscellaneous PD worker async handlers, mainly max timestamp synchronization for transaction correctness and min-resolved-ts reporting.

Important APIs/functions: `Runner::handle_update_max_timestamp` and `Runner::handle_report_min_resolved_ts`.

Control flow: max-ts handling clones PD/concurrency/causal-ts/shutdown handles and spawns an async loop. While `txn_ext.max_ts_sync_status` still equals the initial status and shutdown is false, it either flushes the causal timestamp provider or obtains a TSO from PD, then updates `ConcurrencyManager::max_ts`. On success it atomically flips the low success bit; on repeated failure it logs at a throttled interval. A failpoint can delay the future by one second. Min-resolved-ts reporting sends an async PD request and logs failure.

State and persistence: no local persistence. Durable correctness is indirect: max-ts advancement prevents future reads/writes on a new leader from using timestamps older than prior leader reads. `max_ts_sync_status` filters stale async completions.

Dependencies/integration: used by `TxnContext::require_updating_max_ts`, depends on PD client TSO/min-resolved-ts APIs, `ConcurrencyManager`, optional RawKV API v2 `CausalTsProviderImpl`, global timer, and YATP remote spawning.

Risks: if PD/causal-ts calls fail indefinitely, leadership remains with stale status until another transition or shutdown; requests may be blocked by higher-level checks. The status compare-exchange means only the currently relevant transition can mark success.

Test signals: no local tests. Failpoint `delay_update_max_ts` supports timing tests.
