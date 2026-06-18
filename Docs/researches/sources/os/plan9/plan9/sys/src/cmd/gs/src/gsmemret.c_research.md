# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmemret.c

Implements `gs_memory_retrying_t`, a wrapper allocator that retries allocation failures after invoking a recovery closure. Initialization installs a forwarding/retrying procedure table, sets the target allocator, inherits the library context, points `non_gc_memory` at itself, and installs a default no-retry recovery procedure.

Allocation, resize, string allocation, struct allocation, array allocation, and root registration use the `RETURN_RETRYING` loop: call the target, and if it returns null while recovery says retry is allowed, call the recovery procedure and retry. Free, status, object type/size, unregister, enable-free, and consolidation simply forward to the target.

`stable` lazily wraps the target stable allocator in a retrying allocator if the stable target differs. This wrapper provides a generic low-memory recovery hook without changing allocator clients.
