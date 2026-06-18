# sources/user-network-fs/nfs-ganesha/src/SAL/state_share.c

Purpose: Implements NLM share reservation management when `_USE_NLM` is enabled. It maintains counted share access/deny modes, reopens files with FSAL share-deny flags, and removes share state from owner, NSM client, file, and export lists.

Important APIs/types/functions: `remove_nlm_share()`, `state_nlm_share()`, `state_share_wipe()`, and `state_export_unshare_all()`. It operates on `state_t`, `state_owner_t`, `state_nlm_client_t`, `state_nlm_share`, `fsal_openflags_t`, and FSAL access masks.

Control flow: `state_nlm_share()` locks object state, updates per-mode access/deny counters for share or unshare, recomputes union access/deny masks, and exits early if the union did not change. If unshare removes the last access mode, it removes all share list memberships and lets the state reference close the file. Otherwise it builds FSAL open flags, performs `test_access()`, calls `fsal_reopen2()` to apply open/share-deny mode, and, for a first active share, links the state into the owner, NSM client, file, and export share lists. Wipe/export cleanup iterate those lists and call `state_nlm_share(..., OPEN4_SHARE_ACCESS_ALL, OPEN4_SHARE_DENY_ALL, ..., unshare=true)`.

State and persistence behavior: Share reservations are in-memory counted state associated with the `state_t`. The active share keeps a `state_t` reference and NSM client reference, and list nodes connect it to owner/client/file/export cleanup paths. No durable persistence is performed here; NLM recovery interactions are through NSM client state and cleanup callbacks.

Dependencies and integration points: Depends on FSAL `test_access` and `fsal_reopen2`, export manager locks, NLM owner/client/NSM structures, SAL state references, and the object `STATELOCK`. Integrates with `state_wipe_file()`, `state_nlm_notify()`, and export release cleanup.

Risks: Counter underflow is guarded only by logging when unshare does not match an existing count; callers can still request mismatched unshares. `remove_nlm_share()` assumes list membership is valid and must be called exactly once for active shares. `state_nlm_share()` unlock path must handle FSAL errors after local counters were tentatively changed, so share counter consistency depends on this path being called with valid protocol sequencing. Export cleanup loops use an error limit and fatal on repeated failure.

Test signals: Cover repeated share/unshare counts, `OPEN4_SHARE_ACCESS_ALL` and `OPEN4_SHARE_DENY_ALL`, final unshare closing/removing state, access-denied and share-denied FSAL reopen failures, reclaim flags, file wipe, NSM client cleanup, and export unshare-all under stale object references.
