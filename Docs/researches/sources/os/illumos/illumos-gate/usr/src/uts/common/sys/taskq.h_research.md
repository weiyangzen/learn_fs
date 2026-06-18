# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/taskq.h

## Purpose
Defines the public kernel task queue interface for asynchronous work dispatch.

## Main Interfaces
- Types:
  - opaque `taskq_t`
  - `taskqid_t`
  - `task_func_t`
- Creation flags:
  - `TASKQ_PREPOPULATE`
  - `TASKQ_CPR_SAFE`
  - `TASKQ_DYNAMIC`
  - `TASKQ_THREADS_CPU_PCT`
  - `TASKQ_DC_BATCH`
  - `TASKQ_THREADS_LWP`
- Dispatch flags:
  - `TQ_SLEEP`
  - `TQ_NOSLEEP`
  - `TQ_NOQUEUE`
  - `TQ_NOALLOC`
  - `TQ_FRONT`
- `TASKQID_INVALID`.
- Kernel APIs:
  - initialization and MP initialization
  - create variants including instance, proc, and SDC-backed taskqs
  - `taskq_dispatch()`
  - wait/wait-by-id, destroy, empty, suspend/resume, membership check
  - `nulltask()`
- Global `system_taskq`.

## Dependencies And Relationships
Includes `sys/types.h` and `sys/thread.h`. Implementation details live in `taskq_impl.h`.

## Research Notes
`TQ_SLEEP` and `TQ_NOSLEEP` intentionally match kmem allocation semantics. Public flags occupy bits 0-15; implementation flags are reserved elsewhere.
