# sources/user-network-fs/samba/source3/torture/bench_pthreadpool.c

## Purpose
Small torture benchmark for Samba's `pthreadpool_pipe` implementation. It measures repeated submit/finish cycles using a no-op job and reports failure on pool, submission, completion, or destruction errors.

## Important APIs, Types, and Functions
`null_job()` is the empty worker callback. `run_bench_pthreadpool(int dummy)` initializes a pool with one worker, loops `torture_numops` times calling `pthreadpool_pipe_add_job()` and `pthreadpool_pipe_finished_jobs()`, destroys the pool, and returns boolean success.

## Control Flow
The benchmark initializes the pool, submits one no-op job, waits for exactly one finished job, and repeats. On any nonzero add/init error or negative finished-jobs result, it prints an error and breaks. After the loop, it requires the final `ret` to equal `1`, then destroys the pool and returns whether destroy succeeded.

## State and Persistence
No persistent state. Runtime state is the pool object, loop counter, returned job ID, and global `torture_numops` controlling workload size.

## Dependencies and Integration Points
Depends on `../lib/pthreadpool/pthreadpool_pipe.h`, torture `proto.h`, global torture settings, and diagnostic output via `d_fprintf(stderr, ...)`. It is integrated as a torture command/benchmark rather than production smbd behavior.

## Risks
The final `ret != 1` check assumes the last `pthreadpool_pipe_finished_jobs()` returns one completed job; if `torture_numops` is zero, the benchmark returns false because `ret` is still the init result. The benchmark serializes submit/wait with a one-thread pool, so it tests overhead and correctness more than parallel throughput.

## Test Signals
Run with positive `torture_numops`, zero operations, injected pool init/add/finish failures, and under leak/thread sanitizers to validate pool destruction and no-op callback execution.
