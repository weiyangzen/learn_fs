## sources/security-integrity/audit-userspace/audisp/plugins/af_unix/queue.h

Purpose: queue API for `audisp-af_unix`.

It declares opaque `struct queue`, open/close, append/peek/drop, length/max/capacity, and empty checks, with compiler allocation/access annotations. State is hidden in queue implementation. Dependencies are `stdbool.h`, `sys/types.h`, and common attribute macros. Risks are ownership semantics controlled by `take_memory` and no concurrency contract. Tests are local queue unit-style cases or plugin backpressure tests.
