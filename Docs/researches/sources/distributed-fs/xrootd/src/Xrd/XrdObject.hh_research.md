## sources/distributed-fs/xrootd/src/Xrd/XrdObject.hh

Purpose: provides generic singly linked queue templates used by XRootD package objects. Queues can push at the front, pop from the front, and optionally age out queued objects through scheduler jobs implemented in `XrdObject.icc`.

Important APIs/types/functions: `XrdObject<T>` wraps an item pointer, next pointer, and queue timestamp. `XrdObjectQ<T>` inherits `XrdJob` and provides `Pop()`, `Push()`, `Set(inQMax, agemax)`, scheduler/trace `Set()`, and `DoIt()`. Queue limits use `MaxinQ`, `MininQ`, and `Maxage`.

Control flow: producers allocate `XrdObject<T>` nodes and `Push()` them. If the queue is above `MaxinQ`, pushed item payloads are deleted. Consumers call `Pop()` to retrieve payload pointers. Time-managed cleanup is configured through `Set()` and runs as a scheduled job.

State/persistence: queue state is memory-only: `First`, `Count`, current age, size limits, scheduler pointer, trace pointer, and trace flag. Payload ownership transfers to queue on push.

Dependencies/integration: depends on `XrdJob`, `XrdSysMutex`, `XrdScheduler`, `XrdSysTrace`, and the inline implementation file `XrdObject.icc`.

Risks: overflow behavior deletes `Node->Item` but not obviously the node in the inline `Push()` body shown here, so callers must understand ownership. The queue is LIFO despite comments about adding to either end; details may be in `XrdObject.icc`. Cleanup requires `Set()` at least once.

Test signals: test push/pop ordering, max queue deletion behavior, scheduled age cleanup, trace integration, and empty pop.
