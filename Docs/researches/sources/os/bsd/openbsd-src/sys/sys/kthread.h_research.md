# File Research: sources/os/bsd/openbsd-src/sys/sys/kthread.h

This kernel-only header declares kernel thread creation and exit helpers.

Kernel APIs:
- `kthread_create`
- `kthread_create_deferred`
- `kthread_run_deferred_queue`
- `kthread_exit`

Behavior and integration:
- `kthread_create` accepts a function, argument, optional created proc pointer, and thread name.
- `kthread_exit` is marked `__noreturn__`.

Risk notes:
- Deferred creation queues allow threads to be created after initial conditions are ready; callers must not assume immediate execution.
