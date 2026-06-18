# sources/test-tools/stress-ng/stress-mq.c

Purpose: implements `mq`, a POSIX message queue IPC stressor. It creates one queue, forks sender/receiver roles, exercises normal and timed send/receive paths, queue attributes, notification registration, and many invalid-call cases.

Important APIs/types/functions: `stress_msg_t` is the queue payload. `stress_mq_invalid_open()` probes invalid `mq_open()` attributes and cleans up if they unexpectedly succeed. `stress_mq()` owns queue sizing, creation, fork, parent sender loop, child receiver loop, verification, and cleanup. Optional Linux paths exercise `lseek`, `fstat`, invalid `mmap`, `poll`, and direct `read` on queue descriptors.

Control flow: setup determines `mq-size`, clamps it against `/proc/sys/fs/mqueue/msg_default` when available, retries smaller sizes on open failure, and computes an absolute timeout for timed operations. The receiver child optionally registers varied `mq_notify()` events, probes invalid opens/unlinks/descriptors, then alternates `mq_receive()` and `mq_timedreceive()` while validating priorities and optional per-priority message ordering. The parent periodically gets/sets attributes, sends messages with random priorities via `mq_send()` or `mq_timedsend()`, probes invalid descriptors/sizes/priorities, increments bogo operations, then kills the child and unlinks the queue.

State and persistence: the POSIX queue persists by name until explicitly unlinked; the stressor unlinks it at cleanup and removes any temporary invalid-open queue names. Parent/child verification counters are in process memory.

Dependencies and integration: requires `mqueue.h`, librt, and POSIX MQ support; uses affinity, fork retry, kill wait, scheduler settings, signal ignore, stress-ng settings and verification flags.

Risks and test signals: host MQ limits can cause resource skips, and timed calls depend on clock availability. Useful signals are successful queue create/unlink, bogo increments, optional ordered payload verification, expected skips for ENOSYS/ENOSPC, and no leaked queue names.
