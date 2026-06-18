# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/TarContainerPacker.java

## Purpose
`TarContainerPacker` packs and unpacks key-value container data for copy/import/export as a compressed tar containing descriptor, checksum metadata, DB data, and chunks.

## Important APIs, Types, And Functions
It implements `ContainerPacker<KeyValueContainerData>` with `pack`, `unpackContainerData`, and `unpackContainerDescriptor`. Static helpers `getDbPath` and `getChunkPath` map schema-aware archive roots. Constants define `container.yaml`, `db`, and `chunks` archive paths.

## Control Flow
`pack` wraps compression, tars the container file, optional checksum tree file, schema-specific DB data, and chunks directory. `unpackContainerData` clears stale temp directories, extracts DB/chunks/checksum entries through `innerUnpack`, verifies descriptor checksum, persists the descriptor in RECOVERING state under the temp metadata path, then atomically moves the temp directory into the destination if empty. Unknown archive entries fail fast.

## State And Persistence
It writes real container directory trees, DB dump files, chunk files, checksum files, and a RECOVERING descriptor. Schema v3 maps DB content to `DatanodeStoreSchemaThreeImpl.getDumpDir`; older schemas map to per-container DB files.

## Dependencies And Integration Points
It integrates `Archiver`, Commons Compress/IO, `CopyContainerCompression`, `ContainerDataYaml`, `ContainerUtils`, `ContainerChecksumTreeManager`, `KeyValueContainerLocationUtil`, and schema-v3 DB dump utilities. `KeyValueHandler` invokes it through `KeyValueContainer` import/export methods.

## Risks And Test Signals
Risks include path traversal protections depending on `extractEntry`, non-empty destination races, missing descriptor, checksum mismatch, schema-v3 dump path mistakes, and partial temp cleanup. Tests should cover v1/v2/v3 round trips, descriptor-only extraction, checksum inclusion, unknown entry rejection, RECOVERING state persistence, and destination-already-exists errors.
