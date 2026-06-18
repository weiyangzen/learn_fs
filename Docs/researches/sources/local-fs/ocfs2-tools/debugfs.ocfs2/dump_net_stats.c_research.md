# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/dump_net_stats.c

## Role

`dump_net_stats.c` reads and prints o2net per-node send/receive timing statistics from debugfs or a saved stats file.

## Input Format

It reads `/sys/kernel/debug/o2net/stats` by default or a user-provided file. Each record carries a protocol version, node number, send count, acquire/send/wait nanosecond totals, receive count, and process-time total.

## Output

It prints per-node send and receive message rates and microseconds-per-message breakdowns for acquire, transmit, wait, total send, and receive processing. With an interval, it computes deltas against the previous sample and repeats until count is exhausted or interrupted.

## Risk Areas

Only protocol version 1 is understood. The function still requires debugfs discovery even when a saved path is supplied. Counts and timing are derived from cumulative kernel counters, so counter resets or malformed captures can produce misleading deltas.
