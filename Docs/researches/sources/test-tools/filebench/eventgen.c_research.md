## sources/test-tools/filebench/eventgen.c

### Purpose
`eventgen.c` implements Filebench's shared event producer used by rate-limiting flowops. It generates events at a configured frequency and signals consumers waiting on shared memory condition variables, enabling workload throttles for events, operations, IOPS, and bandwidth.

### Important APIs, Types, And Functions
The external API consists of `eventgen_init`, `eventgen_setrate`, and `eventgen_reset`. The internal `eventgen_thread` is the long-lived producer loop. It reads `filebench_shm->shm_eventgen_hz`, updates `shm_eventgen_enabled`, increments `shm_eventgen_q`, and signals `shm_eventgen_cv` under `shm_eventgen_lock`.

### Control Flow
`eventgen_init` creates a detached-style pthread running `eventgen_thread` and exits the process on creation failure. The thread waits until a rate variable is configured, then fetches the current rate with `avd_get_int`. For positive rates it sleeps for ten periods, computes elapsed nanoseconds with `gethrtime`, derives how many events elapsed, caps queue depth to about five seconds of events, increments the shared event queue, signals the condition variable, and repeats forever. `eventgen_reset` clears the queue before worker execution starts.

### State And Persistence
All operational state is in shared memory through `filebench_shm`: configured rate, enabled flag, event queue, mutex, and condition variable. The producer has a local `last` timestamp, but no persistent storage. Events accumulated before worker start are intentionally dropped by `eventgen_reset`.

### Dependencies And Integration Points
It includes `filebench.h`, `vars.h`, `eventgen.h`, `flowop.h`, and `ipc.h`. Consumer flowops in `flowop_library.c` use the shared event queue for rate limiting. `fbtime.c` provides a portable `gethrtime` fallback when the OS lacks Solaris `gethrtime`.

### Risks
The thread runs forever and has no explicit shutdown path in this file. A zero or negative rate causes the loop to continue without sleeping in the `else` branch after reading a non-null rate, which can spin if the configured rate is nonpositive. Queue depth is capped only before adding `count`, so a large delayed wake can still overshoot the cap. Rate changes are read without a separate configuration lock beyond shared variable access assumptions.

### Test Signals
Test signals include thread creation success, event queue growth matching configured rates over wall-clock intervals, reset clearing queued events, consumers waking on `shm_eventgen_cv`, and behavior under rate changes or disabled/null rates.
