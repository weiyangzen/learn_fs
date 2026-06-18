# `sources/storage-engines/tikv/components/raftstore/src/store/memory.rs`

## Purpose
This file defines raftstore memory tracing roots and helpers for entry-cache eviction decisions. It lets raftstore account memory for peers, apply FSMs, entry cache, router state, raft messages, and raft entries, then uses process high-water detection to decide when the entry cache should be evicted.

## Important APIs, Types, and Functions
- `MEMTRACE_ROOT` defines the raftstore memory trace tree.
- `MEMTRACE_PEERS`, `MEMTRACE_APPLYS`, `MEMTRACE_ENTRY_CACHE`, `MEMTRACE_RAFT_ROUTER_ALIVE`, `MEMTRACE_RAFT_ROUTER_LEAK`, `MEMTRACE_APPLY_ROUTER_ALIVE`, `MEMTRACE_APPLY_ROUTER_LEAK`, `MEMTRACE_RAFT_MESSAGES`, and `MEMTRACE_RAFT_ENTRIES` expose subtraces used by FSM/router/message code.
- `get_memory_usage_entry_cache` returns the summed entry-cache trace, with a failpoint override.
- `needs_evict_entry_cache` returns true when entry-cache usage exceeds a configured ratio of near-high-water process memory, with a failpoint override and zero-ratio disable behavior.

## Control Flow
The trace tree is initialized lazily. Code elsewhere records trace events against the relevant subtrace. `needs_evict_entry_cache` first honors a failpoint, returns false if the configured ratio is effectively zero, asks `memory_usage_reaches_near_high_water` whether process memory is near the high-water mark, and compares entry-cache traced bytes against `usage * ratio`.

## State and Persistence Behavior
All state is process-local memory accounting. There is no disk persistence. Correctness depends on callers adding and subtracting trace events reliably; for example `RaftRouter::send_raft_message` subtracts message heap size on failed forwarding.

## Dependencies and Integration Points
The file depends on `tikv_alloc::mem_trace`, failpoints, and `tikv_util::sys::memory_usage_reaches_near_high_water`. It is re-exported via `store/mod.rs` and consumed by raftstore FSM, entry cache, router, and apply paths.

## Risks and Edge Cases
- If trace increments/decrements are unbalanced elsewhere, eviction decisions become inaccurate.
- `needs_evict_entry_cache` only considers eviction when the process is near high-water memory; large entry cache below that threshold will not trigger eviction.
- A ratio below `f64::EPSILON` disables eviction, which is intentional but can surprise config validation.
- Failpoints can force mock usage or eviction behavior in tests.

## Test Signals
There are no local tests in this file. Useful tests would cover disabled ratio, mocked entry-cache usage, mocked high-water status, and trace balance in router/entry-cache callers.
