## sources/storage-engines/wiredtiger/src/include/generation_inline.h

Purpose: this inline header provides the fast-path accessors for WiredTiger generation counters. The comment notes a future cleanup goal to move all generation functions into one file.

Important APIs/types/functions: `__wt_gen(session, which)` returns the connection-wide generation for a resource by relaxed volatile atomic load from `S2C(session)->generations[which]`. `__wt_gen_next(session, which, genp)` atomically increments the connection generation and optionally returns the new value. `__wt_session_gen(session, which)` returns the current session's generation for the selected resource by relaxed volatile atomic load from `session->generations[which]`.

Control flow: resource managers call `__wt_gen_next` when moving a resource class to a new generation. Sessions enter and leave generations through non-inline functions declared in `extern.h`; checks compare per-session generation values with connection generation values to decide whether old resources remain active. The inline functions keep reads and increments cheap because they are used in frequent synchronization paths.

State and persistence behavior: the state is in-memory generation counters on the connection and sessions. Generations are not durable, but they protect lifecycle decisions for resources that can back durable data, including data handles, metadata, page references, and cache structures.

Dependencies and integration points: it depends on `WT_SESSION_IMPL`, `S2C(session)`, the `generations` arrays, and atomic helpers from `gcc.h`. It integrates with `generation.h` cookies, session generation enter/leave functions, handle sweep, hazard-pointer style lifetime control, and shutdown/drain logic.

Risks: relaxed loads are intentional but require callers to provide the necessary synchronization and comparison discipline. Using the wrong `which` index or forgetting to publish session generation entry/exit can cause premature reclamation or leaks. `__wt_gen_next` uses a seq-cst add helper, so changing it to a weaker operation would need careful review.

Test signals: handle lifecycle stress, session close while resources are active, generation drain timeout tests, schema/drop/rename concurrent with cursors, and sanitizer use-after-free detection validate this area.
