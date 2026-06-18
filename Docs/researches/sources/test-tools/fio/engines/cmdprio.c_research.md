# sources/test-tools/fio/engines/cmdprio.c

Purpose: Shared command-priority helper for fio asynchronous engines such as libaio and io_uring, handling option parsing, per-IO random priority assignment, and priority-specific completion latency stats.

Important APIs/functions: Public functions are `fio_cmdprio_init()`, `fio_cmdprio_cleanup()`, and `fio_cmdprio_set_ioprio()`. Internal helpers parse `cmdprio_bssplit`, generate block-size priority descriptors, assign `clat_prio_index`, allocate `thread_stat.clat_prio`, and compute whether an IO should receive a command priority.

Control flow: Init records options, detects whether percentage or block-size split mode is active, rejects simultaneous modes, defaults missing class to real-time, then builds either per-direction percentage entries or sorted block-size descriptors. During queueing, an engine calls `fio_cmdprio_set_ioprio()`: it finds the applicable percentage, draws a random 0-99 value from `td->prio_state`, and if selected stores `io_u->ioprio` plus the precomputed completion-latency priority index. Cleanup frees per-block-size arrays and clears the options pointer.

State/persistence: `struct cmdprio` owns generated descriptor arrays; option storage belongs to the engine option struct inside `td->eo`. Thread stats receive allocated per-priority latency buckets.

Dependencies/integration: Uses fio option parsing (`str_split_parse`, `split_parse_prio_ddir`), ioprio helpers, latency stat allocation, random state, and read/write direction predicates. Trim is intentionally ignored.

Risks: Error paths rely on cleanup to free partially built descriptors. The bssplit lookup is linear over block sizes in the hot path. Percentage sums above 100 are rejected per block size, but zero or unmatched block sizes silently use default priority.

Test signals: Cover mutually exclusive option rejection, default priority class, read/write enablement filtering, bssplit percentages by block size, clat priority bucket creation, and deterministic selection using seeded `prio_state`.
