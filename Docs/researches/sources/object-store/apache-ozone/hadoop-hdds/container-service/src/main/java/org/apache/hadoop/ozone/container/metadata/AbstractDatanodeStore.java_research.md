## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/AbstractDatanodeStore.java

Purpose: Implements common datanode container store behavior over RocksDB: opening schema definitions, wrapping tables, providing safe iterators, and exposing block/finalize iteration.

Important APIs and functions: `initDBStore()` applies schema-specific DB options, builds the DB, initializes metadata, block, finalize, and last-chunk tables, and wraps normal tables in `DatanodeTable` to disable raw iteration. `getBlockIterator()` and `getFinalizeBlockIterator()` return filtering iterators. `checkTableStatus()` fails fast on missing tables. Nested iterators filter keys by `KeyPrefixFilter` and cache the next value.

Control flow and state: The store keeps both wrapped tables for normal point operations and unwrapped iterator-capable tables for controlled iteration. Schema v1/v2 cap total WAL size; schema v3 customizes obsolete file deletion and JMX naming. Iterator classes scan underlying RocksDB iterators and apply byte-level prefix filters before exposing blocks or local IDs.

Persistence and dependencies: Inherits RocksDB lifecycle from `AbstractRDBStore`. Integrates with `DatanodeSchema*DBDefinition`, `DatanodeConfiguration`, `DBStoreBuilder`, `Table`, `BlockData`, `ChunkInfoList`, and container `BlockIterator`.

Risks: Direct table iteration is intentionally disabled except through controlled paths; bypassing this can mix schema prefixes. Iterator `nextBlock()` recurses after `hasNext()`, which is shallow but should remain correct. Missing finalize/last-chunk tables are schema-dependent. Schema v3 prefix filters must align with fixed-length key encoding.

Test signals: Open schema one/two/three stores, verify table wrappers and iterator-capable tables, iterate normal and filtered blocks, iterate finalize local IDs, handle missing tables, enforce unsupported raw iteration, and close/flush/compact through inherited DB manager APIs.
