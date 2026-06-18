## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DatanodeTable.java

Purpose: Wraps an HDDS `Table` for datanode container stores while disabling direct iteration to prevent schema-unsafe scans.

Important APIs and functions: Most CRUD, batch, range, prefix-delete, dump, and load methods delegate to the wrapped table. `iterator(KEY prefix, IteratorType type)` is final and throws `UnsupportedOperationException`. `getName()`, estimated counts, existence checks, and read-copy operations are pass-throughs.

Control flow and state: The class holds a single wrapped `Table` reference. It enforces iteration policy at runtime while allowing controlled iterators to use separate unwrapped table handles inside `AbstractDatanodeStore`.

Persistence and dependencies: It does not add persistence behavior; it delegates to RocksDB-backed table implementations. It depends on HDDS table, batch, codec, iterator type, and metadata key filter abstractions.

Risks: New `Table` methods must be delegated or deliberately blocked when the interface evolves. Code that requires iteration must obtain schema-aware iterators from `DatanodeStore`, not this wrapper. Since prefix-delete and dump are still delegated, callers must pass schema-correct prefixes.

Test signals: Verify put/get/delete/batch/range delegation, direct iterator failure, prefix delete and dump delegation, table name/count pass-through, and schema-aware iterator access through store APIs.
