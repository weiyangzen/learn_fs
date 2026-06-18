# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sleepq.h

## Role

Defines common sleep queue structures for traditional sleep queues and turnstile constituents.

## Key Interfaces

- `sleepq_t` stores the first sleeping thread.
- `sleepq_head_t` combines a sleep queue with a dispatcher lock for a hash bucket.
- Kernel constants/macros:
  - `NSLEEPQ` = 2048
  - `SQHASHINDEX(X)` computes a mixed pointer hash.
  - `SQHASH(X)` locates the bucket head.
- Exports `sleepq_head[]`.
- Kernel functions insert, wake one/all by channel, unsleep, dequeue, and unlink threads.

## Risk Notes

Sleep queue hashing and locking are scheduler/synchronization infrastructure. Pointer hashing must preserve bucket distribution, and callers must observe dispatcher-lock expectations around queue mutation.
