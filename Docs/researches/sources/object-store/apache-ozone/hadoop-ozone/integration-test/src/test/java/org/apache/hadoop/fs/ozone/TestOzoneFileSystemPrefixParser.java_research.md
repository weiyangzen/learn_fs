# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFileSystemPrefixParser.java

Purpose: verifies the offline OM `PrefixParser` correctly classifies volumes, buckets, intermediate directories, missing directories, files, and directories in an FSO bucket.

Important APIs/types/functions: setup creates a three-DN cluster, an FSO O3FS bucket, directory `/a/b/c/d/e`, and file `/a/b/c/file1`. `testPrefixParsePath` stops the cluster and parses paths against the OM DB directory. `assertPrefixStats`, `testPrefixParseWithInvalidPaths`, and `verifyPrefixParsePath` compare parser counters.

Control flow: after cluster stop, parse an existing directory parent, an existing file, invalid volume, invalid bucket, and an invalid intermediate directory path. Each parse uses volume, bucket, OM DB path, and target path.

State and persistence behavior: relies on RocksDB state persisted by OM before shutdown. The parser reads DB files directly rather than live OM services.

Dependencies and integration points: uses `PrefixParser`, `OMStorage.getOmDbDir`, `MiniOzoneCluster`, O3FS, and FSO bucket layout.

Risks: stopping the cluster before parsing is required to inspect stable DB state. Parser counters are sensitive to FSO metadata layout and path-depth interpretation.

Test signals: catches regressions in offline prefix diagnostics for existing and missing path components, invalid volume/bucket handling, and file-vs-directory classification.
