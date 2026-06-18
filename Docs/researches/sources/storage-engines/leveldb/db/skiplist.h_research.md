# sources/storage-engines/leveldb/db/skiplist.h

Purpose: provides LevelDB's arena-allocated concurrent-reader skip list template used by memtables. It supports externally synchronized single-writer insertion and lock-free reads/iteration while nodes remain alive for the whole list lifetime.

Important APIs and types: `SkipList<Key, Comparator>`, nested `Node`, nested `Iterator`, `Insert`, `Contains`, iterator `Seek`, `SeekToFirst`, `SeekToLast`, `Next`, `Prev`, `FindGreaterOrEqual`, `FindLessThan`, `FindLast`, `RandomHeight`, and `NewNode`.

Control flow: insertion finds predecessor nodes at each level, generates a random height with probability 1/4 for each extra level, updates `max_height_` if needed, initializes the new node's links with relaxed stores, then publishes it through predecessor release stores. Reads traverse from current max height down to level 0 using acquire loads.

State and persistence behavior: no disk state. Memory is owned by an `Arena`; nodes are never individually deleted, which is the key safety property for concurrent readers. `max_height_` may be observed stale or ahead by readers, but head links make either observation safe.

Dependencies and integration: depends on `util/arena.h` for lifetime, `util/random.h` for height generation, and comparator functors. It underpins memtable ordering, so comparator correctness and no duplicate insertion are required.

Risks and edge cases: `Insert` asserts duplicates are absent rather than handling them. `Prev` is O(log n) because there are no backward links. The constructor creates the head node with key `0`, so instantiated key types must accept that construction path in practice. Memory ordering is intentionally minimal and fragile if multi-writer insertion is attempted without external locking.

Test signals: `skiplist_test.cc` validates empty behavior, randomized set equivalence, forward/backward iteration, and concurrent single-writer/multiple-reader visibility invariants.
