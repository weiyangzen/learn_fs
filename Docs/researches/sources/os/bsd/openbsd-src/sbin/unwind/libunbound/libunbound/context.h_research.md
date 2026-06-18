# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/libunbound/context.h

`context.h` defines libunbound's internal `ub_ctx` and `ctx_query` structures plus the private pipe command protocol used between API callers and background workers.

`struct ub_ctx` owns async query/result tubes and locks, configuration/finalization state, background process/thread identity, allocator-cache freelist, shared module environment, module stack, local zones, random seed state, optional event-base integration, outstanding-query rbtree, and async query count.

`struct ctx_query` represents one outstanding synchronous, asynchronous, or event-based lookup. It stores the query number, cancellation state, callback pointers, callback argument, raw answer packet, validation security status, handling worker, and allocated `ub_result`.

The header declares context finalization, query allocation/deletion/comparison, alloc-cache obtain/release, and serialization/deserialization helpers for new-query, answer, cancel, quit, and command probing. It couples libunbound's public API layer to the worker/tube protocol and module environment internals.
