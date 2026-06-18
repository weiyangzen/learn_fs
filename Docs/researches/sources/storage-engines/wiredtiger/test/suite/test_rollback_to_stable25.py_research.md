# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable25.py

Purpose: exhaustive scenario test for RTS interactions with RLE cells, uniform versus heterogeneous writes, updates versus deletes, eviction at different times, and rollback stable times. It filters meaningless scenario combinations before running.

Important APIs/types/functions: direct `wttest.WiredTigerTestCase` subclass with `verify_rts_logs`. Defines `is_meaningful`, `writes`, `evict`, and `check`. Uses `filter_scenarios`, `make_scenarios`, cursor removes/updates, debug eviction, timestamped transactions, `WT_NOTFOUND`, and `conn.rollback_to_stable`.

Control flow: creates a row-store table, pins timestamps at 2, writes endpoint rows at 5, applies scenario-selected writes at 10/20/30, optionally evicts after each phase, rolls back to stable 15 or 25, then checks expected visibility at read timestamps 10/20/30.

State and persistence behavior: endpoints bookend an RLE-sized range so reconciliation can generate or preserve RLE cells. RTS must correctly instantiate or prune data depending on whether stable time falls before or after updates/deletes.

Dependencies and integration points: integrates scenario filtering with WiredTiger reconciliation details and cursor search semantics. It is tightly coupled to RLE/time-window behavior.

Risks: scenario explosion is controlled by `is_meaningful`; modifying write-type semantics without updating the filter can create invalid or redundant cases. RLE formation is an implementation detail and may change with reconciliation.

Test signals: `check` verifies endpoints, expected values for every interior key, and `WT_NOTFOUND` for expected deletions at each timestamp after RTS.
