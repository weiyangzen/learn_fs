# sources/storage-engines/wiredtiger/src/support/generation.c

## Purpose
Implements WiredTiger's generation-based reclamation system. Sessions publish generation numbers while accessing resources; replacers advance connection generations and wait until older session generations drain before reclaiming old objects. The file also manages per-session stashed memory that can be freed once no active session can reference its generation.

## Important APIs, Types, and Functions
- `__wt_gen_init` initializes all connection generations to 1.
- `__wt_gen_next_drain(session, which)` advances a generation and waits for older users.
- `__wt_gen_active(session, which, generation)` checks whether any session can still see a generation.
- `__wt_session_gen_enter` and `__wt_session_gen_leave` publish and clear a session's generation with required memory barriers.
- `__wt_stash_add`, `__wt_stash_discard`, and `__wt_stash_discard_all` defer and later free memory by generation.
- Internal callbacks for `__wt_session_array_walk` implement drain, oldest, and active scans.

## Control Flow
Initialization stores generation 1 for all resources. Enter loops storing the current connection generation into the session slot, uses a full barrier, and repeats if the connection generation changed during publication. Draining increments a connection generation and walks sessions; for each session with an older nonzero generation, it spins briefly, then sleeps, logging minute-level waits and optionally enabling extra verbose categories shortly before configured timeout. Oldest/active scans read session generation slots with acquire barriers.

Stash add appends a pointer/length/generation to the session stash, updates connection stashed byte/object counters, and opportunistically discards older entries. Discard computes the oldest active generation for that resource, frees stash entries older than it, subtracts counters, overwrites freed memory, and compacts the stash list when many entries were removed.

## State and Persistence Behavior
No persistent data is written. Runtime state includes connection generation counters, per-session generation slots, generation drain timeout settings, verbose levels temporarily raised near timeout, per-session stash arrays, and connection stashed memory counters. Memory reclamation is delayed until generation visibility proves safety.

## Dependencies and Integration Points
Used by split, hazard, eviction, checkpoint, snapshot, and transaction commit generation users. Depends on session-array walking from `session_helper.c`, atomic operations, memory barriers, verbose/error infrastructure, sleep/yield primitives, and WiredTiger allocation/free helpers.

## Risks
Memory ordering is the main risk. If enter/leave barriers are weakened or scans read values out of order, old objects can be freed while still visible. Draining while the current session holds the target generation triggers a panic for self-deadlock. Long drains can indicate leaked generation entries or stuck sessions. Stash ordering assumes callers generally add nondecreasing generations; out-of-order entries delay reclamation.

## Test Signals
Tests should stress concurrent enter/leave with generation advancement, active/oldest detection, self-deadlock diagnostics, drain timeout logging, stash add/discard counters, discard-all at connection close, and resource-specific users such as split/hazard/checkpoint generations under sanitizer and stress configurations.
