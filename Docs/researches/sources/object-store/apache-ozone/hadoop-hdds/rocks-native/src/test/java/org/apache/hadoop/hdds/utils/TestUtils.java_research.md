<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/test/java/org/apache/hadoop/hdds/utils/TestUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/test/java/org/apache/hadoop/hdds/utils/TestUtils.java

Purpose: Test-only helper for generating representative optional lower/upper bound values from a sorted key set. It supports RocksDB SST iterator tests that need many boundary combinations without enumerating every key.

Important APIs/types/functions: `TestUtils` is a final utility class with a private constructor. `getTestingBounds(SortedMap<String, Integer>)` returns `List<Optional<String>>` containing a key below the first key, the first key, decile samples from the sorted key set, a key above the last key, and `Optional.empty()` to represent an unbounded side. It depends on `StringUtils.getLexicographicallyLowerString` and `getLexicographicallyHigherString`.

Control flow and state: The method is stateless. For non-empty maps it copies keys into an ordered list, samples ten positions with `(i * size / 10) - 1`, converts each boundary to `Optional.of`, then appends an empty optional. Empty input produces only the unbounded marker.

Dependencies and integration points: Used by native/raw SST iterator tests and checkpoint differ SST set tests to exercise RocksDB iterate bounds. The helper assumes the sorted map order matches the string comparison used by RocksDB/string codecs.

Risks: For very small maps, decile arithmetic repeats indexes, but the intermediate `HashSet` deduplicates. Boundary output order is not stable because the set is unordered; tests must treat it as a sampling set, not as a deterministic sequence.

Test signals: Coverage comes indirectly through `TestManagedRawSSTFileIterator` and `TestSstFileSetReader`, which use all lower/upper bound pairs and validate emitted keys against map filtering.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/test/java/org/apache/hadoop/hdds/utils/TestUtils.java -->
