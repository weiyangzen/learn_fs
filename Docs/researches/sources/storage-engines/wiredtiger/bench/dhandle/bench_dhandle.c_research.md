# sources/storage-engines/wiredtiger/bench/dhandle/bench_dhandle.c

## Purpose
This benchmark stresses WiredTiger data-handle lifecycle behavior under dynamic table creation, dropping, checkpoints, reads, and updates. It grows to a target table count, keeps a configured active window, drops older tables, and measures operation latencies.

## Important APIs, Types, and Functions
Core types are `SHARED`, `THREAD_ARGS`, and `WORK_ITEM`. Key functions are `main`, `bench_dhandle`, `bench_dhandle_run`, `creator`, `queuer`, `worker`, `checkpointer`, and `shuffle`. It uses WiredTiger `WT_CONNECTION`, `WT_SESSION`, `WT_CURSOR`, test utility allocation/parsing helpers, `TAILQ`, pthreads, and `BENCH_TIMER` macros/functions.

## Control Flow
`main` parses benchmark options and defaults. `bench_dhandle` recreates/open the home and runs the workload. `bench_dhandle_run` starts N worker threads plus creator, queuer, and checkpointer, then periodically aggregates per-thread timers and prints deltas/minute summaries until runtime or active-table completion. The creator creates tables to a time-based target high watermark, inserts first records, advances low/exists/high watermarks, drops obsolete tables, and throttles to creation-time percent. The queuer waits for initial tables, builds work items over active table numbers, marks about 10% as updates, and pushes them under a rwlock. Workers pop work items, open cursors, search or update table key 0, and reset sessions. The checkpointer periodically calls `session->checkpoint`.

## State, Persistence, and Dependencies
Persistent state is the WiredTiger home with thousands of table files and statistics logs. Shared state includes table watermarks, queue length, done/started/checkpoint flags, checkpoint number, and per-thread shared timers updated with memory barriers. Dependencies are POSIX pthreads, WiredTiger internal/test utilities, queue macros, and `bench_timer`.

## Integration Points, Risks, and Test Signals
The benchmark integrates schema churn, dhandle open/close, checkpointing, and concurrent table operations. Test signals are printed operation counts and per-op times; the queue overflow path fails by setting `done`. A notable risk is `shuffle`: the loop initializes `i = n - 1` but tests `i < 0`, so it appears never to shuffle. This can bias queue order and weaken randomization.
