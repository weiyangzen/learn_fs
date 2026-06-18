# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestTarContainerPacker.java

## Purpose
`TestTarContainerPacker` validates tar-based container replication packaging and unpacking for key-value containers across all test schema/layout combinations and every `CopyContainerCompression` mode. It checks descriptor-first archive layout, metadata DB/chunk extraction, checksum sidecar preservation, stream closure, and path traversal defenses.

## Important APIs, types, and functions
The tests exercise `TarContainerPacker.pack`, `decompress`, `unpackContainerDescriptor`, `unpackContainerData`, `compress`, `getDbPath`, and constants such as `CONTAINER_FILE_NAME`, `DB_DIR_NAME`, and `CHUNKS_DIR_NAME`. It builds `KeyValueContainerData` and `KeyValueContainer` objects, writes synthetic DB/chunk files, writes the container descriptor YAML, and uses `ContainerChecksumTreeManager` plus `ContainerMerkleTreeWriter`.

## Control flow
`getLayoutAndCompression` generates a Cartesian product of `ContainerTestVersionInfo.getLayoutList()` and `CopyContainerCompression.values()`. The main `pack` test creates a source container tree with metadata DB, chunk file, descriptor, and checksum file; packs it; inspects the tar stream to ensure the descriptor is first; reads only the descriptor; then unpacks data into a destination container path. Additional tests create single-file tar archives with nested relative DB or chunk paths and with traversal-style `../` paths.

## State and persistence behavior
Unpacking must materialize DB and chunk files under the destination container root, preserve source container ID in destination metadata, persist the checksum file, and rewrite the destination container descriptor so its state contains `RECOVERING`. Checksum state is verified by comparing the source and destination Merkle trees. Spy streams assert pack/unpack closes input/output exactly once.

## Dependencies and integration points
The suite integrates Apache Commons Compress tar streams, Ozone replication compression, archive inclusion via `Archiver.includeFile`, checksum tree serialization, and container descriptor files used by datanode startup. It also depends on schema-version injection through `ContainerTestVersionInfo.setTestSchemaVersion`.

## Risks and edge cases
Important risks are malformed archive ordering, resource leaks, losing checksum sidecar state during replication, extracting files outside the destination root via relative paths, and accepting nested valid paths incorrectly. The tests explicitly distinguish `sub/dir/file` as valid from `../file` as invalid.

## Test signals
Signals include tar entry inspection, descriptor byte-for-byte comparison, stream-close assertions, existence/content checks for unpacked files, destination state checks, and Merkle-tree equality through `assertTreesSortedAndMatch`.
