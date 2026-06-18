<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/pom.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/pom.xml

Purpose: Maven module descriptor for Apache Ozone's RocksDB checkpoint differ jar, which packages compaction DAG tracking, compaction log entities, SST utilities, and tests.

Important APIs/types/functions: The artifact is `org.apache.ozone:rocksdb-checkpoint-differ:2.3.0-SNAPSHOT`, parented by `hdds`. Dependencies include Guava graph utilities, protobuf, commons libraries, HDDS common/config/interface/managed-rocksdb/rocks-native, Ratis common, RocksDB JNI, and SLF4J. Test dependencies include Hadoop common, the `hdds-rocks-native` test jar, and HDDS test utilities.

Control flow and state: Build configuration points SpotBugs at the module-local empty exclude filter and disables annotation processing via `maven-compiler-plugin` `<proc>none</proc>`. The `native-testing` profile activates on the `rocks_tools_native` property and extends Surefire's `java.library.path` to the built native RocksDB tooling.

Dependencies and integration points: This POM binds the module to Ozone's managed RocksDB wrappers and native raw SST tooling. Tests that require raw SST support depend on the native profile and system property.

Risks: Native tests can silently skip when the property/library path is missing. The module depends on generated protobuf classes from HDDS interfaces, so schema changes must stay compatible with `CompactionFileInfo` and `CompactionLogEntry` codecs.

Test signals: Run normal module tests plus the `native-testing` profile to cover both managed RocksDB iterator paths and native raw SST tombstone paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/pom.xml -->
