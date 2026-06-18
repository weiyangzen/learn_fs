# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/QueueMapTest_Peek.cpp

Purpose: tests non-destructive `QueueMap::peek` behavior.

Important APIs/types/functions: `QueueMapPeekTest`, fixture helpers `push`, `peek`, `pop`, and keyed `pop`.

Control flow: checks empty peek, repeated peek after one or two pushes, interaction between peek and FIFO pop, and peek after removing the first key directly.

State and persistence behavior: queue-map maintains insertion order; `peek` must not remove entries, while keyed pop updates both map and queue ordering.

Dependencies and integration points: inherits `QueueMapTest`, uses Boost optional I/O helper for assertions, and minimal key/value fixture types.

Risks and test signals: verifies peek idempotence and consistency after keyed removal. It does not cover peeking after capacity-like bulk operations because QueueMap itself does not enforce capacity here.
