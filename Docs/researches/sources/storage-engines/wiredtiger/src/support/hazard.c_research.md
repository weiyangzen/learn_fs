# sources/storage-engines/wiredtiger/src/support/hazard.c

## Purpose
`hazard.c` implements WiredTiger hazard pointers, the per-session mechanism that pins in-memory pages so eviction cannot free a page while another thread is reading or modifying it. It is a core correctness layer between B-tree page access, eviction, and session lifecycle management.

## Important APIs, Types, and Functions
`__wt_hazard_set_func` publishes a hazard pointer for a `WT_REF`, returning `busyp=true` when the page is not safely usable. `__wt_hazard_clear` releases a hazard pointer and panics if the session did not hold it. `__wt_hazard_close` reports and clears leaked hazards during session close. `__wt_hazard_check` walks sessions to find any hazard pointer on a ref, optionally returning the owning session. `__wt_hazard_count` counts this session's hazards for a ref, and `__wt_hazard_check_assert` verifies no hazard remains, optionally waiting. `hazard_grow`, `hazard_get_reference`, and `__hazard_check_callback` are internal helpers.

## Control Flow
Setting a hazard first skips no-evict trees, then checks the ref state for `WT_REF_MEM`. It grows the session hazard array if full, finds or exposes a slot, writes `hp->ref`, issues a full barrier, and rechecks the ref state. If the ref is still memory-resident, the hazard becomes active; otherwise the slot is cleared and the caller sees `busy`. Clearing searches in reverse, release-stores `NULL`, decrements `num_active`, and may reset `inuse` to zero. System-wide checks enter the hazard generation, walk all sessions, and leave the generation after the scan.

## State and Persistence Behavior
Hazard state lives in `session->hazards`: the pointer array, `size`, atomic `inuse`, and `num_active`. Growth allocates a doubled array, release-publishes it, increments the hazard generation, and stashes the old array for deferred freeing through `__wt_stash_add`. Diagnostic builds also store the function and line that set each hazard.

## Dependencies and Integration Points
This file is tightly integrated with B-tree ref states, eviction, session arrays, generation management, statistics, stashed memory reclamation, and diagnostic reporting. Correctness depends on WiredTiger's memory-barrier macros, atomic loads/stores, and the eviction protocol that locks refs before checking hazards.

## Risks
The code is deliberately barrier-heavy because stale ordering can produce use-after-free or out-of-bounds reads after hazard-array growth. `__wt_hazard_clear` panics when a matching ref is absent because continuing would imply an unpinned page was used. Session close tolerates leaked hazards but logs them, which prevents a close-time leak from becoming an eviction pin. Generation entry around global scans is required because another thread can grow and retire a hazard array while eviction is walking it.

## Test Signals
Stress tests should race page access, eviction, splits, and hazard-array growth. Diagnostic tests should verify function/line dump output for leaked hazards. Assertions should cover no-evict btrees, repeated set/clear, clear of missing hazard producing panic, `__wt_hazard_check_assert` with and without wait, and deferred freeing under hazard generation. Eviction tests should demonstrate that a page with any session hazard is not discarded.
