## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DatanodeSchemaOneDBDefinition.java

Purpose: Defines the legacy schema-one datanode container DB layout where block data, metadata, and deleted block records all share RocksDB's default column family.

Important APIs and functions: Static column family definitions `BLOCK_DATA`, `METADATA`, and `DELETED_BLOCKS` all reference the default CF name but use different value codecs. Accessors return those definitions. `getColumnFamilies(String)` and `getColumnFamilies()` expose a multimap so multiple logical tables can map to one physical CF.

Control flow and state: The definition is immutable. Logical table separation is achieved through codecs and key prefixes rather than physical column families.

Persistence and dependencies: Uses `SchemaOneKeyCodec` for mixed long/string keys, `BlockData.getCodec()`, `LongCodec`, and `SchemaOneChunkInfoListCodec`. `DatanodeStoreSchemaOneImpl` wraps the deleted-block table to apply `#deleted#` prefixes.

Risks: Multiple logical tables over one CF can decode unrelated keys with the wrong value codec. Schema-one compatibility depends heavily on key-prefix conventions. Deleted block values may be either old local-ID placeholders or newer chunk-info protobufs.

Test signals: Open existing schema-one DBs, round-trip unprefixed numeric block keys and prefixed metadata/deleted keys, scan deleting blocks, access deleted-block records through the wrapper, and validate mixed logical table definitions on one CF.
