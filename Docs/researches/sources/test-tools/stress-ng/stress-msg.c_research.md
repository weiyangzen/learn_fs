# sources/test-tools/stress-ng/stress-msg.c

Purpose: implements `msg`, a System V message queue IPC stressor. It creates one active queue plus additional resource-pressure queues, sends and receives messages between parent and child, verifies FIFO ordering when possible, and exercises `msgctl`, `msgget`, `msgsnd`, and `msgrcv` edge cases.

Important APIs/types/functions: `stress_msg_t` contains `mtype` and a value/data payload. `stress_msg_get_stats()` exercises `IPC_STAT`, `IPC_SET`, `MSG_STAT_ANY`, `IPC_INFO`, `MSG_INFO`, and invalid `msgctl()` calls. `stress_msgget()` and `stress_msgsnd()` probe unusual invalid arguments. `stress_msg_receiver()` consumes messages with optional type filtering and verification; `stress_msg_sender()` produces messages, periodically reads stats and `/proc/sysvipc/msg`; `stress_msg()` owns queue lifecycle.

Control flow: setup reads `msg-types` and `msg-bytes`, allocates an array for extra queue IDs, creates the main private queue, probes unusual `msgget()` calls, and allocates more queues up to a per-instance cap. After synchronization it forks a receiver pinned near the parent CPU. The sender loop chooses message type, sends with occasional `IPC_NOWAIT`, handles full queues by retrying blocking, increments bogo, and periodically gathers stats. The receiver loops on `msgrcv()`, optionally peeks with `MSG_COPY`, retries expected empty/again errors, and verifies monotonically increasing payloads only when type filtering is disabled. Cleanup kills the child and removes all queues.

State and persistence: System V queues persist in the kernel until `IPC_RMID`; the stressor removes the main and extra queues on all cleanup paths. Per-process counters hold verification state.

Dependencies and integration: requires SysV IPC headers and message queue support; uses affinity, fork retry, kill/wait helpers, scheduler settings, proc reading on Linux, stress-ng settings, bogo counters, and `VERIFY_ALWAYS`.

Risks and test signals: queue limits can produce resource exits, typed receives break FIFO verification by design, and forgotten `IPC_RMID` would leak kernel IPC objects. Signals are created/deleted queue debug logs, ordered verification with `msg-types=0`, exercised stats paths, and cleanup of every allocated queue ID.
