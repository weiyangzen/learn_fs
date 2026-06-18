<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/common/queue.go -->
# Research: sources/user-network-fs/gcsfuse/common/queue.go

Purpose: defines a small generic FIFO queue abstraction and linked-list implementation used by buffered read prefetching to track ordered block work.

Important APIs/types/functions: `Queue[T]` exposes `IsEmpty`, `Peek`, `Push`, `Pop`, and `Len`; `NewLinkedListQueue[T]` returns a `linkedListQueue[T]`; private `node[T]` links items through `start` and `end` pointers with a `size` counter.

Control flow: `Push` appends at the tail and initializes both ends for the first element. `Peek` returns the head without mutation. `Pop` removes the head, resets both pointers when the final element is removed, and decrements length. `Peek` and `Pop` intentionally panic on empty queues.

State and persistence: state is entirely in memory and not synchronized. Queue ordering and `size` are the invariants; no persistence or external resources are involved.

Dependencies: only Go generics and package-local structs. The current major integration point is `internal/bufferedread.BufferedReader.blockQueue`.

Risks: not thread-safe; callers must lock externally. Empty-queue panics are correct for misuse but require callers to guard with `IsEmpty`. If used with mutable pointer values, queue ownership is not copied.

Test signals: `common/queue_test.go` covers construction, FIFO behavior, length, peek non-mutation, empty state, and panics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/common/queue.go -->
