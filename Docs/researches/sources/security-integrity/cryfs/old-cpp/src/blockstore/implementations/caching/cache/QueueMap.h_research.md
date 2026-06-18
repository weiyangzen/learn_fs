# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/QueueMap.h

Purpose: Implements an addressable FIFO queue: entries can be pushed in queue order, popped by key, popped from the front, and peeked from the front.

Important APIs and types: `QueueMap<Key, Value>` exposes `push`, `pop(key)`, `pop()`, `peekKey`, `peek`, and `size`. It stores an `unordered_map<Key, Entry>` plus a sentinel node for a doubly linked list. `Entry` manually stores `Value` in aligned byte storage.

Control flow: `push` emplaces an `Entry` in the map with links at the tail, initializes its key pointer and placement-news the value, then splices it before the sentinel. `pop(key)` finds the map entry, unlinks it, moves/releases its value, erases the map entry, and returns the value. `pop()` removes the sentinel's next entry. Peek methods return optional references to the front key/value.

State and persistence behavior: State is all in-memory. The destructor iterates remaining entries and calls `release` to run value destructors. Map nodes are relied on for stable addresses so linked-list pointers remain valid.

Dependencies and integration points: Used by `Cache` to track insertion/eviction order while supporting keyed lookup. Depends on Boost optional and cpp-utils assertions/macros.

Risks: Manual lifetime management is delicate: `Entry::release` must be called exactly once for initialized entries. `push` throws `logic_error` for duplicate keys. `peekKey` returns a reference wrapped in `boost::optional`, so callers must not outlive the map mutation. No internal locking is provided; synchronization is the caller's responsibility.

Test signals: Direct tests should cover ordering, duplicate key rejection, pop by key, pop empty, value destruction on erase/destructor, and pointer/reference validity under unordered_map growth. Current validation is likely through cache tests.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/QueueMap.h` completely for this pass (122 lines, 3427 bytes).
