## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/ContainerKeyPrefixCodec.java

Purpose: `ContainerKeyPrefixCodec` serializes `ContainerKeyPrefix` keys for the container-to-key-prefix table.

Important APIs and types: singleton `get`, `toPersistedFormat`, `fromPersistedFormat`, `copyObject`, `getTypeClass`. It uses `LongCodec`, UTF-8, underscore delimiter, `ArrayUtils`, and `StringUtils`.

Control flow: serialization writes the 8-byte container ID first. If a key prefix is present, it appends `_` plus UTF-8 key prefix. If key version is not -1, it appends `_` plus 8-byte version. Deserialization assumes the full persisted form exists: first 8 bytes container ID, bytes between delimiters for key prefix, and final 8 bytes for version.

State and persistence: no mutable state. The byte format controls RocksDB key ordering and seek behavior for `ContainerKeyPrefix` tables.

Dependencies and integration points: used by Recon container metadata DB definitions/implementations. Prefix-seek keys may serialize with only container ID or missing version, but the deserializer is designed for complete DB entries.

Risks and edge cases: key prefixes containing underscores are safe because deserialization uses fixed first/last byte positions, but malformed or prefix-only raw data cannot be deserialized correctly. `copyObject` returns the same instance, assuming immutability. Serialization with key prefix but version -1 produces a form that `fromPersistedFormat` does not explicitly support.

Test signals: codec tests should cover full round trip, container-only prefix seek serialization, key prefixes with underscores/UTF-8, malformed byte arrays, and ordering expectations.
