# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/txg.h

This header declares transaction group constants, handles, per-TXG object lists, and synchronization APIs.

Core definitions:
- `TXG_CONCURRENT_STATES` is 3 for open/quiescing/syncing.
- `TXG_SIZE` is 4, `TXG_MASK` indexes circular arrays, `TXG_INITIAL` is the first txg, and `TXG_DEFER_SIZE` is 2.
- `txg_handle_t` records the per-CPU hold object and assigned txg.
- `txg_node_t` embeds per-TXG next pointers and membership flags in dirty objects.
- `txg_list_t` stores a lock, embedded-node offset, owning SPA, and per-TXG heads.

Public API surface:
- Init/fini and sync-thread start/stop.
- Hold open txg, release to quiesce/sync, register commit callbacks, delay or kick sync.
- Wait for synced/open txgs, including signal-aware wait, stalled/sync-waiting queries, and verification.
- Per-TXG list create/destroy, empty checks, add/head/tail/remove/remove-this/member/head/next.

Risk-sensitive invariants:
- TXG arrays are circular and must use the proper txg index.
- Objects may be members of different per-TXG lists simultaneously only through the explicit `txg_node_t` membership fields.
- Hold/release ordering drives quiesce/sync progress and must be balanced by transaction users.
