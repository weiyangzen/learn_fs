# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestFSODirectoryPathResolver.java

Purpose: Tests `FSODirectoryPathResolver` reconstruction of absolute FSO directory paths from object IDs. Important APIs and types include mocked `Table<String, OmDirectoryInfo>`, `Table.KeyValueIterator`, `OmDirectoryInfo`, `Optional<Set<Long>>`, `Path`, and `OM_KEY_PREFIX`.

Control flow: The helper returns a mocked directory table whose prefix iterator decodes the requested parent object ID and yields child directory rows from an in-memory parent-to-children map. The test builds a multi-level tree, asks for paths for selected object IDs, compares the returned map to expected absolute paths, then includes an unreachable ID and expects `IllegalArgumentException`.

State and persistence behavior: All directory metadata is mocked/in-memory. The resolver state under test is traversal from bucket root object ID through directory table prefixes to build object-ID-to-path mappings.

Dependencies and integration points: FSO directory table key format, object ID hierarchy, path normalization, and snapshot diff/path reporting that needs human-readable paths. Risks are that the mock table only models iterator-by-prefix behavior needed by this resolver. Test signals are exact path mapping for root and nested IDs, result size, and exception message for missing IDs.
