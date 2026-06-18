# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestKeyValueBlockIterator.java

Purpose: verifies `BlockIterator<BlockData>` behavior over key-value container metadata tables across schema/layout variants and schema V3 key-separator settings.

Important APIs/types/functions: `db.getStore().getBlockIterator(containerID)`, filtered `getBlockIterator(containerID, KeyPrefixFilter)`, `BlockIterator.hasNext`, `nextBlock`, `seekToFirst`, `KeyValueContainerData.getDeletingBlockKeyFilter`, `containerPrefix`, and helper `createContainerWithBlocks`.

Control flow: `provideTestData()` duplicates the full `ContainerTestVersionInfo` matrix for empty and configured schema V3 key separators. `initTest()` toggles schema and separator config, then `setup()` creates a container and opens its DB. Tests populate block table rows with unprefixed, deleting, and synthetic second-prefix keys. They assert default iteration skips deleting-prefixed blocks, repeated `hasNext()` is idempotent, `seekToFirst()` resets iteration, `nextBlock()` throws a specific `NoSuchElementException` at EOF, deleting filters return only deleting blocks, and arbitrary future prefixes work.

State and persistence behavior: the file writes `BlockData` rows directly into the container's RocksDB block table. It does not write chunk files; block rows contain minimal `ChunkInfo`. Prefix construction includes `containerData.containerPrefix()` so schema-specific key formats are exercised.

Dependencies and integration points: depends on `MutableVolumeSet`, `BlockUtils`, `DatanodeConfiguration`, Ozone constants for deleting-key prefix, metadata key filters, and JUnit parameterization. It protects store iterator behavior that scanner, deletion, and listing code depend on.

Risks and test signals: strong signal for iterator cursor semantics and prefix filtering in RocksDB-backed stores. HashMap iteration is used when creating prefix groups, but expected IDs are tracked by prefix and sorted insertion per prefix, so tests focus on filter correctness rather than global key ordering.
