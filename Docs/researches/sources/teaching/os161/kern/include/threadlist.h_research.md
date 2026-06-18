# File Research: sources/teaching/os161/kern/include/threadlist.h

Defines an intrusive doubly linked list specialized for `struct thread`. Lists contain permanent head and tail sentinel nodes, eliminating end-case handling. Each thread embeds a `threadlistnode`, and each node carries `tln_self` to recover the owning thread without pointer arithmetic.

Exports node/list init and cleanup, emptiness checks, add/remove at both ends, insertion before/after existing threads, arbitrary removal, and forward/reverse iteration macros.

The important invariant is that `struct threadlist` must not be assigned or memcpy’d after initialization because sentinel links point inside the structure. Correct use also depends on each thread being on at most one list through its embedded node.
