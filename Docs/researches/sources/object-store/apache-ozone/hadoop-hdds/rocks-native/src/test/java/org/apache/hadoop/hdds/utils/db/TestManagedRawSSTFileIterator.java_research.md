<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/test/java/org/apache/hadoop/hdds/utils/db/TestManagedRawSSTFileIterator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/test/java/org/apache/hadoop/hdds/utils/db/TestManagedRawSSTFileIterator.java

Purpose: Native-only parameterized tests for `ManagedRawSSTFileReader` and `ManagedRawSSTFileIterator`, validating raw SST iteration across key/value formats, tombstones, large strings, special characters, iterator modes, and lower/upper bounds.

Important APIs/types/functions: The class is enabled only when the `rocks_tools_native` system property is true. `init()` loads the native raw SST library. `createSSTFileWithKeys` writes a temporary SST with sorted keys, using operation type `0` for deletes and non-zero for puts. `keyValueFormatArgs` combines multiple key/value format cases with every `IteratorType`.

Control flow and state: Each test builds a `TreeMap<Pair<String,Integer>,String>`, writes it as an SST file, opens a raw reader, generates sampled bounds via `TestUtils.getTestingBounds`, and for every lower/upper pair compares iterator output with an independently filtered expected map. The assertions honor `IteratorType`: keys or values may be intentionally null when the mode does not read them.

Dependencies and integration points: Relies on RocksDB native tooling, managed RocksDB option/env wrappers, `ManagedSlice` bounds, `StringCodec`, and Apache Commons `Pair`/random string helpers. It tests the raw iterator used by checkpoint differ pruning code and `SstFileSetReader.getKeyStreamWithTombstone`.

Risks: Tests are skipped unless native tooling is enabled, so CI lanes without the property do not cover raw tombstone iteration. Large random prefix cases increase confidence in buffer handling and escaping, but expected ordering still depends on RocksDB's byte/string ordering matching Java `TreeMap` ordering for the generated data.

Test signals: Strong signals include all `IteratorType` modes, null/newline/quote content, long key/value prefixes, delete and put entries, and exhaustive sampled bound pairs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/test/java/org/apache/hadoop/hdds/utils/db/TestManagedRawSSTFileIterator.java -->
