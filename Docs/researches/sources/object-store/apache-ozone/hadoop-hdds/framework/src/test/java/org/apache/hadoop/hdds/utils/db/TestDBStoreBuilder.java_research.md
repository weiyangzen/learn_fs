<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestDBStoreBuilder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestDBStoreBuilder.java

Purpose: tests `DBStoreBuilder` validation and RocksDB store construction with tables, writes, DB profiles, column-family options, and auto-compaction settings.

Important APIs/types/functions: `DBStoreBuilder.newBuilder`, `setName`, `setPath`, `addTable`, `setProfile`, `build`, `DBStore`, `RDBStore`, `Table`, `DBProfile.DISK`, `DBColumnFamilyDefinition`, `DBDefinition.WithMap`, `ManagedColumnFamilyOptions`, `RocksDatabase.ColumnFamily`, and `disableAutoCompactions`.

Control flow: early tests assert missing name/path combinations throw `IOException`. Open/close and write tests build stores in temp directories, add tables, put/get random byte-array keys/values, and verify empty second tables. Column-family option tests define a custom DB definition with per-table options, build an `RDBStore`, inspect column-family descriptors, and assert non-default settings were applied. Parameterized compaction tests build with config controlling auto-compaction and assert each column family reflects it.

State and persistence behavior: creates real RocksDB stores under temp paths, writes table data, inspects column-family metadata, and closes stores to release native resources. Uses a system property for DB config directory in setup.

Dependencies and integration points: integrates Ozone configuration, RocksDB-backed `RDBStore`, table definitions/codecs, managed CF options, random test data, and DB profiles.

Risks: native RocksDB resources require reliable close. Random keys are fine for uniqueness but make failures less reproducible. Builder validation and column-family options are high risk because misconfiguration affects DB layout/performance.

Test signals: asserts builder exceptions, successful open/close, duplicate table handling, byte-array persistence, empty secondary table, disk profile writes, column-family count, custom CF option effect, and configured auto-compaction flag per column family.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestDBStoreBuilder.java -->
