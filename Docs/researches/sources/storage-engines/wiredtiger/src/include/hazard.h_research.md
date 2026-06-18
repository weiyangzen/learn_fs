## sources/storage-engines/wiredtiger/src/include/hazard.h

Purpose: this header defines the callback cookie used when walking sessions to find active hazard pointers. Hazard pointers protect pages or references from being reclaimed while a session may still use them.

Important APIs/types/functions: `WT_HAZARD_COOKIE` carries `search_ref`, an optional returned owning session pointer `ret_session`, an optional returned hazard slot `ret_hp`, and walk counters `walk_cnt` and `max`. Related functions are declared in `extern.h`, including `__wt_hazard_check`, `__wt_hazard_check_assert`, `__wt_hazard_set_func`, `__wt_hazard_clear`, and `__wt_hazard_close`.

Control flow: a caller that wants to know whether a `WT_REF` is protected populates `search_ref` and walks sessions. The callback increments `walk_cnt`, scans hazard slots up to `max`, and records the matching session and hazard pointer when found. Diagnostic/assert paths can wait for hazards or fail if an expected hazard state is violated.

State and persistence behavior: the cookie is transient. The protected state is in-memory page/reference ownership. Hazard correctness indirectly protects persistent correctness by preventing eviction, split, discard, or reconciliation code from freeing or reusing page structures while readers still depend on them.

Dependencies and integration points: it depends on `WT_REF`, `WT_SESSION_IMPL`, `WT_HAZARD`, and session-walk infrastructure. It integrates with page eviction, tree walk, cursor positioning, page release, and diagnostic verification.

Risks: incomplete scanning or stale returned pointers can cause use-after-free, eviction stalls, or false-positive busy results. `walk_cnt`/`max` must reflect the configured hazard slot capacity. Hazard operations are concurrency-sensitive and must be paired correctly with page acquire/release paths.

Test signals: eviction stress under concurrent readers, cursor traversal during page splits, diagnostic hazard assertions, sanitizer use-after-free detection, and workloads that force hazard table growth or saturation are useful.
