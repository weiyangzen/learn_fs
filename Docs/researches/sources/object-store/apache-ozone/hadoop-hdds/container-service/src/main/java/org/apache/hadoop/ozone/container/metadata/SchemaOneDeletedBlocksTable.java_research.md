## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/SchemaOneDeletedBlocksTable.java

Purpose: Adapts schema-one deleted-block operations to look like an unprefixed logical table while storing keys with `#deleted#` in the shared default column family.

Important APIs and functions: Overrides put, batch put, delete, batch delete, delete range, existence, get, read-copy, and range methods to prefix keys before delegation. `getRangeKVs()` ignores caller filters and uses the deleted-key filter, then strips prefixes from returned keys.

Control flow and state: The class extends `DatanodeTable` and has no mutable state beyond the wrapped table. Prefix/unprefix helpers handle nulls and remove the first deleted prefix.

Persistence and dependencies: It persists `ChunkInfoList` values through the schema-one default CF. It uses `KeyPrefixFilter.newFilter("#deleted#")` to prevent regular block keys from being returned as deleted blocks.

Risks: `String.replaceFirst()` treats the prefix as a regex; the current prefix is safe but future special characters would matter. Ignoring user-supplied range prefixes is intentional but can surprise callers. Double-prefixing by callers would produce bad physical keys.

Test signals: Put/get/delete with unprefixed keys, range scans returning unprefixed keys, delete range, null key handling, collision with non-deleted block keys, and caller-supplied prefix/filter ignored for deleted table scans.
