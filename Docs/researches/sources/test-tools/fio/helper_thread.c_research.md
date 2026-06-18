# sources/test-tools/fio/helper_thread.c

## Purpose
Implements fio's background helper thread. The helper performs periodic runtime work such as disk utilization sampling, status output, steadystate checks, ramp-period checks, log sample scheduling, and final log flushing, while receiving explicit actions from the main thread.

## Important APIs, Types, and Functions
Public entry points are `helper_thread_create`, `helper_thread_exit`, `helper_thread_destroy`, `helper_reset`, `helper_do_stat`, and `helper_should_exit`. Internal state is `struct helper_data` with an exit flag, action pipe, `sk_out`, thread id, and startup semaphore. `struct interval_timer` describes recurring callbacks. Key helpers include pipe/socket compatibility wrappers, `submit_action`, `wait_for_action`, `reset_timers`, `eval_timer`, `helper_thread_main`, and Windows `pipe_over_loopback`.

## Control Flow
Creation allocates helper data, sets up disk and steadystate support, creates a nonblocking pipe or loopback socket pair, starts `helper_thread_main`, and waits on a startup semaphore. The helper blocks signals, initializes timer precision, assigns socket output, resets interval timers, then loops until an exit flag, timer callback error, or `A_EXIT`. Each iteration waits for a pipe action or timeout, evaluates periodic timers, handles forced stat output, calculates the next log deadline, and prints thread status for non-backend runs. Exit closes timerfd if present, writes logs, and drops socket output.

## State and Persistence Behavior
Persistent user-visible effects are periodic status output, disk-util sampling state, steadystate results, and final log files. In-memory state is global `helper_data`, `sleep_accuracy_ms`, and optional `timerfd`. `helper_do_stat()` is documented as callable from signal-handler context and routes work through the pipe action.

## Dependencies and Integration Points
Depends on fio core timing, logging, diskutil, status/stat output, steadystate, semaphores, `sk_out`, platform pipe/socket APIs, timerfd when available, and Valgrind DRD annotations. The main runtime creates the helper around job execution and uses reset/stat/exit APIs to coordinate it.

## Risks
`submit_action()` asserts on short writes, which is deliberate but harsh if the action pipe is full or closed. `helper_thread_create()` leaks the allocated helper data on some pipe/thread creation failures. Timer callbacks share a single return path, so any nonzero callback return stops the helper. `helper_data->exit` is volatile but not an atomic synchronization primitive. The Windows pipe emulation has several socket setup failure paths.

## Test Signals
Tests should create and destroy the helper repeatedly, inject `A_RESET` and `A_DO_STAT`, cover timerfd and non-timerfd builds, validate no blocked signals are handled in the helper, and run under sanitizers for failure paths. Integration signals are stable status intervals, disk-util updates, and log flushes at run end.
