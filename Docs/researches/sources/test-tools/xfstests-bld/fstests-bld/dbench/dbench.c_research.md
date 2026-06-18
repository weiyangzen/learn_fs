# sources/test-tools/xfstests-bld/fstests-bld/dbench/dbench.c

Purpose: main process for dbench/tbench benchmark execution. It parses options, starts child worker processes, synchronizes launch, reports throughput and latency, and prints final results.

Important APIs and functions: global `struct options options`, static `open_loadfile`, `sem_cleanup`, `sig_alarm`, `show_one_latency`, `report_latencies`, `create_procs`, `show_usage`, `process_opts`, and `main`.

Control flow: `main` parses popt options, sets warmup, and calls `create_procs`. `create_procs` opens the load file, allocates shared memory for child structures, initializes a System V semaphore barrier, forks worker processes, waits until all are ready, releases the barrier, schedules periodic `SIGALRM` reports, waits for children, and prints latency summaries. `sig_alarm` handles warmup cutoff, timelimit stop, cleanup progress, throughput, and latency sampling.

State and persistence: uses shared memory for child metrics, a System V semaphore for launch synchronization, global timing values, and global `throughput`. Child workers mutate filesystem/socket state via `child_run`.

Dependencies and integration: depends on libpopt, dbench utility functions, `shm_setup`, backend `nb_*` operations, and `child.c`. Build-time macros provide `VERSION`, `DATADIR`, EA support, and TCP defaults.

Risks: signal handler performs substantial non-async-signal-safe work including `printf`. Semaphore creation test treats ID 0 as failure. Exit handling assumes `WEXITSTATUS` is meaningful without first checking normal exit.

Test signals: periodic output reports active clients and MB/sec, final throughput line includes client/process counts and max latency, and nonzero child exits fail the run.
