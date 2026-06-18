# sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote-queue.h

Purpose: Declares the private queue interface used by the z/OS remote audisp plugin to pass BER-encoded audit requests between threads.

Important APIs, types, and functions: Includes `<lber.h>` for `BerElement` and declares `init_queue(unsigned int size)`, `enqueue(BerElement *)`, `dequeue(void)`, `nudge_queue(void)`, `increase_queue_depth(unsigned int size)`, and `destroy_queue(void)`.

Control flow: The header does not implement control flow; it exposes a minimal lifecycle contract: initialize, enqueue/dequeue between producer and consumer, optionally wake the consumer, grow capacity, and destroy.

State and persistence: The interface implies module-global queue state hidden in the C file. There is no persistence or explicit queue handle, so only one queue instance can exist in a process.

Dependencies and integration points: Integrated only with the z/OS remote plugin implementation. The direct `BerElement *` type couples the queue to liblber and makes it unsuitable as a generic audisp queue abstraction.

Risks and edge cases: Because `enqueue()` is void, callers cannot observe full-queue drops or know whether ownership transferred. `dequeue()` has no timeout or stop argument; callers rely on `nudge_queue()` and external state, but the implementation waits for non-NULL queue slots. These choices matter for clean shutdown and memory ownership.

Test signals: Header coverage should come from queue C tests or plugin integration tests. The absence of a return code on `enqueue()` is a testability limitation.
