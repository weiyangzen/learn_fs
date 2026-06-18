# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestTypedTable.java

Purpose: Deep tests for `TypedTable` codec behavior, key ordering, empty keys/values, and iterator modes over typed metadata keys.

Important APIs/types/functions: `TypedTable`, `Codec`, `ByteArrayCodec`, `StringCodec`, `LongCodec`, `ContainerID.getCodec`, `TableIterator`, `Table.KeyValueIterator`, iterator modes `NEITHER`, `KEY_ONLY`, `VALUE_ONLY`, `KEY_AND_VALUE`, `keyIterator`, and `valueIterator`.

Control flow: Setup creates several RocksDB column families and tracks closeables. Tests exercise empty byte-array and string keys/values with both codec-buffer and byte-array codec paths, compare `ContainerID` and `Long` persisted key formats by reopening tables with alternate key codecs, populate thousands of generated boundary/random keys, and validate prefix and non-prefix iterators across all iterator read modes.

State and persistence behavior: Real RocksDB persistence is used to prove codec-stable key serialization across different logical key types. Iterator tests destructively remove entries from expected maps as they are observed.

Dependencies and integration points: Integrates HDDS codecs, SCM `ContainerID`, table cache type selection, RocksDB column families, and leak detection.

Risks: Heavy random key generation can lengthen runs and reduce determinism. Prefix tests rely on stringified container IDs and map ordering. The compatibility test assumes `ContainerID` and `Long` codecs intentionally share persisted representation.

Test signals: Strong signal for typed codec compatibility, empty value handling, iterator read-mode laziness, key/value iterator alignment, and prefix scan correctness.
