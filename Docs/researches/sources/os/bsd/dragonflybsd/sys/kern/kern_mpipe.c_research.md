# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_mpipe.c

## Purpose

`kern_mpipe.c` implements `malloc_pipe`, a bounded preallocation/cache layer over `kmalloc()` for subsystems that need a nominal reserve, optional maximum growth, optional zeroing, optional interrupt-reserve allocation, and optional deferred callback notification when buffers become available.

## Main Responsibilities

- Initializes a pipe with nominal and maximum buffer counts in `mpipe_init()`.
- Preallocates nominal buffers and optional construct callbacks.
- Starts a support kernel thread when `MPF_CALLBACK` is enabled.
- Destroys a pipe and all cached buffers with `mpipe_done()`.
- Provides nonblocking, callback, wait-hint, and blocking allocation APIs.
- Returns buffers to the cache or frees overflow buffers with `mpipe_free()`.

## Core Data Model

`struct malloc_pipe` stores the malloc type, object size, flags, derived malloc flags, construct/deconstruct callbacks, nominal array capacity, maximum total capacity, current free count, current total count, callback queue, pending flag, support thread pointer, and LWKT token. The free array is LIFO and sized to the nominal count.

Queued callbacks are `struct mpipe_callback` objects containing function and two arguments. They are processed by the support thread only when cached buffers are available.

## Allocation and Free Behavior

`_mpipe_alloc_locked()` first consumes a cached free buffer. If the cache is empty and the maximum count is reached, or a previous malloc attempt failed in the wait loop, it returns `NULL`. Otherwise it attempts a nonblocking `kmalloc()` and constructs the new buffer on success.

`mpipe_alloc_nowait()` simply tries allocation under the token. `mpipe_alloc_callback()` queues a callback if two allocation attempts fail. `mpipe_wait()` waits until a future allocation is likely to succeed but does not guarantee it. `mpipe_alloc_waitok()` sleeps on the pipe until allocation succeeds.

`mpipe_free()` returns buffers to the LIFO array while space remains, optionally zeroing them unless cached data or no-zero flags are set. It wakes callback and allocation waiters as needed. If the nominal cache is full, it deconstructs and frees the buffer and decrements total count.
