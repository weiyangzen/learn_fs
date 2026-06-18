# sources/storage-engines/tikv/tests/failpoints/cases/test_memory_usage_limit.rs

## Purpose
This file validates raftstore behavior when memory usage crosses high-water limits: committed entries still apply, entry cache can be evicted aggressively, and raft append rejection/unreachable behavior is controlled by memory pressure.

## Important APIs, Types, and Functions
- `test_memory_usage_reaches_high_water`, `test_evict_entry_cache`, `test_memory_full_cause_of_raft_message`, and `test_evict_early_avoids_reject` are the main tests.
- `MEMTRACE_ENTRY_CACHE` is used as a memory accounting signal.
- Helper functions `setup_server_cluster`, `put_n_entries`, `add_message_filter`, `add_filter_append_and_unreachable`, and `wait_msg_counter` set up learners and count raft messages.
- Failpoints include `memory_usage_reaches_high_water`, `needs_evict_entry_cache`, `needs_reject_raft_append`, `mock_memory_usage`, `mock_memory_usage_high_water`, and `mock_memory_usage_entry_cache`.

## Control Flow
The first test forces high-water state and ensures repeated puts still apply. The entry-cache eviction test blocks normal log GC cleanup on one store, grows the cache with large values, then enables high-water and eviction failpoints and confirms cache size drops despite long lifetime. The message rejection test adds a learner, counts `MsgAppend` and `MsgUnreachable`, forces append rejection, and expects both counters to rise. The final test first disables eviction to grow cache, then simulates near-high-water memory so early eviction prevents `MsgUnreachable`.

## State and Persistence Behavior
The tests separate committed data persistence from volatile raft entry cache accounting. High memory should not prevent committed writes from being applied, but it should evict cache before rejecting append messages when possible. Learner replication state is used to observe rejection behavior through raft messages rather than persisted data only.

## Dependencies and Integration Points
The suite integrates raftstore memory tracing, raft log GC ticks, entry cache eviction ticks, learner replication, `RegionPacketFilter` message callbacks, and memory failpoint instrumentation.

## Risks and Test Signals
Risks include data apply starvation under memory pressure, entry cache not shrinking, premature append rejection, or missing unreachable responses. Signals are successful `must_get_equal`, `MEMTRACE_ENTRY_CACHE.sum()` thresholds, and message counter assertions.
