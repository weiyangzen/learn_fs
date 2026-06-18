# sources/user-network-fs/mergerfs/vendored/moodycamel/concurrentqueue.h

## Purpose

This header vendors Cameron Desrochers' `moodycamel::ConcurrentQueue`, a C++11 header-only multi-producer, multi-consumer queue. It is intended to provide high-throughput lock-free enqueue/dequeue operations for mergerfs or vendored consumers without requiring a compiled library. The design uses per-producer subqueues, fixed-size element blocks, producer/consumer tokens, and atomic coordination rather than one central locked queue.

## Important APIs, Types, And Functions

- `moodycamel::ConcurrentQueueDefaultTraits` configures `size_t`, `index_t`, `BLOCK_SIZE`, initial block-index sizes, implicit producer hash size, explicit consumer rotation quota, `MAX_SUBQUEUE_SIZE`, `MAX_SEMA_SPINS`, allocation hooks, and whether dynamically allocated blocks are recycled.
- `moodycamel::ConcurrentQueue<T, Traits>` is the main public type. Public operations include constructors with preallocation hints, move construction/assignment, `swap`, `enqueue`, `try_enqueue`, `enqueue_bulk`, `try_enqueue_bulk`, `try_dequeue`, token-aware dequeue variants, `try_dequeue_bulk`, `try_dequeue_from_producer`, `size_approx`, and `is_lock_free`.
- `moodycamel::ProducerToken` owns an explicit producer stream. It is movable, non-copyable, has `valid()`, and marks its underlying producer inactive on destruction.
- `moodycamel::ConsumerToken` stores a consumer's current producer selection, desired producer, global rotation offset, and per-producer consumption quota state.
- Internal `ProducerBase`, `ExplicitProducer`, and `ImplicitProducer` implement subqueue-specific enqueue/dequeue behavior. Explicit producers keep a circular linked list of blocks plus a published block index. Implicit producers are looked up by thread ID and use a separate lock-free block-index table.
- Internal `Block` stores `BLOCK_SIZE` in-place `T` objects in aligned raw storage, plus empty flags or a completed-dequeue counter. It is also a node in the queue's lock-free free list.
- Internal `FreeList<N>` is a CAS-based free list with a refcount and a "should be on free list" bit to avoid freeing nodes while another thread is reading the list head.
- `details::ThreadExitNotifier` and `ThreadExitListener` retire implicit producers when a thread exits on platforms where C++11 `thread_local` is enabled.
- `moodycamel::swap` overloads support queue, producer token, consumer token, and internal implicit producer hash-entry swapping.

## Control Flow

Construction initializes atomic queue state, the implicit producer hash if enabled, and an initial block pool sized from either raw capacity or producer/capacity hints. Public implicit `enqueue` resolves the calling thread to an implicit producer through `get_or_add_implicit_producer`; explicit `enqueue` uses the `ProducerToken`'s producer directly. The producer then reserves space at `tailIndex`, allocates or reuses a block if the tail crosses a block boundary, placement-news the element, and finally publishes the incremented `tailIndex` with release ordering.

`try_enqueue` follows the same producer paths with `AllocationMode::CannotAlloc`, so it can fail when block-index growth, block allocation, or capacity growth would be required. Bulk enqueue preallocates all needed block-index entries and blocks first, then constructs elements block by block, reverting partially built state on constructor exceptions.

General `try_dequeue` scans producer subqueues, prefers a heuristically largest non-empty producer, and falls back to all producers if the preferred one races empty. Token-aware dequeue uses `ConsumerToken` rotation: consumers start at different producers, consume up to `EXPLICIT_CONSUMER_CONSUMPTION_QUOTA_BEFORE_ROTATE`, then increment `globalExplicitConsumerOffset` so all token consumers gradually move to the next producer. Producer-specific dequeue bypasses this scan and directly drains one explicit producer.

Both explicit and implicit producers use the same optimistic dequeue pattern: read `tailIndex`, compare `dequeueOptimisticCount - dequeueOvercommit` against the tail, increment the optimistic counter, re-read the tail with acquire ordering, then either claim a `headIndex` slot or repair overcommit. Claimed elements are moved into the caller's output, destroyed in place, and their block slot is marked empty. Implicit blocks are returned to the global free list once all slots are empty; explicit producers keep their circular block list and reuse empty blocks.

Implicit producer lookup hashes a platform-specific thread ID into the current `ImplicitProducerHash`, searches current and previous hash tables, lazily copies older entries forward, and resizes when the table crosses about half full. Thread-exit notification marks implicit producer hash entries reusable with `invalid_thread_id2` and sets the producer inactive for later reuse.

Destruction is explicitly not thread-safe. It walks the producer list, invalidates live tokens, destroys producer-owned elements and block-index structures, frees implicit hash tables, drains the global free list, and destroys the initial block pool.

## State And Persistence Behavior

All state is in memory. Persistent queue state consists of atomics and heap/preallocated structures inside the queue object: producer list tail/count, initial block pool and cursor, global free list, implicit producer hash chain and resize flag, consumer rotation counters, and per-producer head/tail/dequeue counters. Elements are stored in raw block storage and explicitly constructed/destructed.

The queue is movable and swappable only when no other thread is using it. Moving transfers producers, block pools, free lists, and hash state, then calls `reown_producers()` so producer parent pointers refer to the destination queue. Tokens remain semantically attached to the moved queue state, not to the original object address.

Memory allocation is controlled through traits. `aligned_malloc` uses trait `malloc` directly for normal alignments and stores a raw pointer prefix for over-aligned internal types. `RECYCLE_ALLOCATED_BLOCKS` controls whether dynamically allocated blocks go into the free list or return to the heap when no longer owned.

## Dependencies

The header depends on C++11 atomics, type traits, aligned storage assumptions, arrays, threads, mutexes, and platform-specific thread ID strategies. It conditionally uses Windows `GetCurrentThreadId`, Apple `TargetConditionals.h`, Relacy headers for race-detection builds, compiler-specific TLS storage, TSAN suppression attributes, and optional internal debug headers. It has no runtime file, socket, or process persistence.

## Integration Points

Consumers include this header and instantiate `ConcurrentQueue<T>` or `ConcurrentQueue<T, CustomTraits>`. Blocking variants are only forward declared here and are expected to be supplied by the companion blocking queue header. Explicit producer tokens are created from either `ConcurrentQueue` or `BlockingConcurrentQueue` through friend constructors. A custom mergerfs integration can tune block size, initial producer hash size, allocation hooks, max subqueue size, and allocation recycling through a traits subclass.

The source is vendored under `sources/user-network-fs/mergerfs/vendored/moodycamel`, so updates should be treated as third-party upgrades. Local changes to memory ordering, token lifetime, or trait defaults would be high risk.

## Risks And Edge Cases

- Destruction, move, and swap are not thread-safe. External synchronization must prove no producers or consumers are active.
- `ProducerToken` and `ConsumerToken` are non-copyable and queue-specific. Reusing a token after its queue is destroyed or with the wrong moved/swapped queue state is invalid.
- `try_enqueue` is not strictly allocation-free for first-time implicit producer creation, and it can fail if implicit producer hashing is disabled or block/index capacity is insufficient.
- `size_approx()` is only accurate when the queue has stabilized and concurrent operations are not racing the estimate.
- `index_t` wraparound is part of the design, but narrow `index_t` values with high turnover can trigger correctness risks noted in the traits comments.
- The queue does not support element types whose alignment exceeds their size.
- Exception paths try to destroy or revert partially enqueued/dequeued elements, but user-provided `T` move assignment or construction behavior can still affect observable dequeue semantics.
- TSAN may report false positives in lock-free paths; the header suppresses selected functions only when Clang TSAN feature detection is active.
- Platform TLS support controls implicit producer cleanup. Defining `MOODYCAMEL_NO_THREAD_LOCAL` or building on unsupported TLS platforms changes implicit producer reuse behavior.

## Test Signals

Useful validation includes compiling all translation units that include this header with the repository's actual compiler flags, running producer/consumer stress tests with implicit and explicit producers, exercising bulk and single-item APIs, validating `try_enqueue` under constrained preallocation traits, running queue destruction only after joining worker threads, and testing with non-trivial `T` types that throw on construction or assignment. Concurrency tests should cover high producer churn to exercise implicit producer hash resize and thread-exit reuse. Sanitizer results need interpretation because lock-free code may generate TSAN noise.
