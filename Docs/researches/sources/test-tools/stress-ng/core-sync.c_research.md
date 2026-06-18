# sources/test-tools/stress-ng/core-sync.c

## Purpose
`core-sync.c` implements shared PID/state management for coordinated stressor startup, especially `--sync-start`, and provides a PID lookup tree used by parent/reaper logic.

## Important APIs, Types, And Functions
`stress_sync_s_pids_mmap` and `stress_sync_s_pids_munmap` allocate shared `stress_pid_t` arrays. `stress_sync_start_init`, `stress_sync_start_wait_s_pid`, `stress_sync_start_wait`, `stress_sync_start_cont_s_pid`, and `stress_sync_start_cont_list` coordinate child stop/continue behavior using `SIGSTOP`/`SIGCONT`. `stress_sync_init_pids`, `stress_sync_order_pid`, and `struct_sync_find_pid` initialize and organize PID records in a hash-balanced binary tree. The internal `stress_sync_order_pid_hash` reverses PID bits via `core-bitops` helpers.

## Control Flow
Parents mmap shared PID records and initialize them to waiting state. Children set their PID, mark themselves waiting, stop themselves when `OPT_FLAGS_SYNC_START` is active, then mark running once continued. The parent polls the linked list until all live children are waiting or finished, sends `SIGCONT` to each, and waits until states report running or finished. PID tree insertion uses reversed PID bits to avoid a degenerate tree for monotonically increasing PIDs.

## State And Persistence
State is shared anonymous memory containing `stress_pid_t` fields such as PID, child PID, state, tree links, reaped flag, and wait status. It is process-shared but not persistent after munmap/process exit. `stress_sync_start_timeout` arms per-process `alarm()` based on `g_opt_timeout`.

## Dependencies And Integration Points
This module depends on `stress-ng.h`, `core-bitops.h`, `core-sync.h`, `mmap`, signals, shared global flags, and timing helpers. Stressors that fork helper children, including `stress-access.c` and `stress-affinity.c`, use this module to synchronize worker starts and maintain reaper state.

## Risks
The fallback non-atomic state store/load path is intentionally racy and relies on polling tolerance. Stopped children must always be continued or killed during cleanup; otherwise test runs can leave suspended processes. PID-hash collisions are possible because lookup compares only the reversed hash, so correctness depends on the transform being one-to-one for the platform PID width.

## Test Signals
Runtime coverage comes from any stressor using `--sync-start`, plus multi-process stressors such as access and affinity. Failures show up as hung starts, missed SIGCONT, unreaped children, or incorrect PID lookup during cleanup.
