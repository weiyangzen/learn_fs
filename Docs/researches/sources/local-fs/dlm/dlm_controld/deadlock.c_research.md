# File Research: sources/local-fs/dlm/dlm_controld/deadlock.c

## Purpose
Implements a distributed DLM deadlock detection prototype using debugfs lock snapshots, OpenAIS/SaCkpt checkpoints, CPG deadlock-cycle messages, transaction wait-for graph construction, and lock cancellation. In the active daemon path, deadlock dispatch is disabled by surrounding `#if 0` blocks in `cpg.c` and related fields in `dlm_daemon.h`.

## Main Behavior
- Initializes a global checkpoint service handle when deadlock detection is enabled.
- Models lock snapshots as resources (`dlm_rsb`), locks (`dlm_lkb`), and transactions (`trans`).
- Reads local lock state from `/sys/kernel/debug/dlm/<lockspace>_locks`.
- Normalizes local, master, and process-copy lock records so process copies can be combined with master copies.
- Writes local lock snapshots into per-node checkpoints named `dlmdeadlk.<lockspace>.<nodeid>`, with one checkpoint section per resource.
- Reads peer checkpoints, converts packed little-endian lock records, and merges them into the local resource graph.
- Cycle protocol:
  - `send_cycle_start()` asks all members to capture lock state.
  - `receive_cycle_start()` reads local debugfs locks, writes a checkpoint, and broadcasts checkpoint-ready.
  - `receive_checkpoint_ready()` reads a peer checkpoint and marks the peer ready.
  - Once all participating nodes are ready, the lowest node id runs detection.
  - `send_cycle_end()` ends the cycle and triggers cleanup on all nodes.
- Deadlock detection:
  - Builds a transaction list from all locks grouped by `xid`.
  - For each waiting/convert lock, finds incompatible granted/convert locks on the same resource and adds wait-for edges to owning transactions.
  - Repeatedly removes transactions with no wait-for dependencies, assuming they can complete.
  - Remaining transactions imply deadlock.
  - Chooses a transaction others wait on, sends `DLM_MSG_DEADLK_CANCEL_LOCK` for its blocked lock(s), and reduces again.
- `receive_cancel_lock()` opens the lockspace through libdlm and calls `dlm_ls_deadlock_cancel()` for the target lkid.
- Handles membership changes during a cycle by purging departed nodes' locks and recalculating the lowest detector node when needed.

## Integration Points
- Depends on `libdlm.h`, `dlm_ls_deadlock_cancel()`, DLM debugfs output, and OpenAIS/SaCkpt APIs.
- Sends DLM CPG messages through `dlm_send_message()`.
- Uses lockspace fields that are currently compiled out in `dlm_daemon.h` under `#if 0`.

## Risks and Notes
- The file references `cfgd_enable_deadlk`, which is not part of the active option set in the read headers, reinforcing that this code is disabled/stale.
- The checkpoint buffer is a fixed 10 MiB global buffer; oversized lock state is logged and truncated by packing limits.
- Debugfs line parsing depends on kernel debug output format.
- The detector cancels one transaction candidate, not necessarily the globally optimal victim.
- Because active CPG dispatch for deadlock messages is disabled, this file should be treated as dormant research/prototype code unless re-enabled with corresponding struct fields and options.
