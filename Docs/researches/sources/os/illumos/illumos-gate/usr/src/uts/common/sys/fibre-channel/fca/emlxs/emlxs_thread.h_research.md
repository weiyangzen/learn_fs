# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_thread.h

## Purpose

Defines lightweight thread and task-queue state structures used by the `emlxs` driver.

## Main Definitions

- `EMLXS_MAX_TASKQ_THREADS` is `4`.
- `emlxs_thread_t`: doubly linked thread object with HBA pointer, kernel thread pointer, flags, function pointer, two arguments, mutex, and condition variable.
- `emlxs_taskq_thread_t`: singly linked taskq worker object with parent taskq pointer, kernel thread pointer, flags, function pointer, argument, mutex, and condition variable.
- `emlxs_taskq_t`: fixed array of taskq threads plus HBA pointer, get/put queues, counters, open flag, and separate get/put locks.
- Thread flags:
  - `EMLXS_THREAD_INITD`
  - `EMLXS_THREAD_STARTED`
  - `EMLXS_THREAD_ASLEEP`
  - `EMLXS_THREAD_BUSY`
  - `EMLXS_THREAD_KILLED`
  - `EMLXS_THREAD_ENDED`
  - `EMLXS_THREAD_TRIGGERED`
  - `EMLXS_THREAD_RUN_ONCE`

## Integration Notes

This header defines only data structures and flags. Thread lifecycle, queue operations, and synchronization semantics live in implementation files.

## Risks and Gotchas

- The task queue uses fixed storage for four worker slots; callers must not assume dynamic scaling.
- `emlxs_thread_t` has two argument pointers while taskq workers have one; callbacks must match the implementation’s dispatch convention.
- Separate get/put locks imply producer/consumer coordination outside this header; misuse can corrupt queue heads or counts.
