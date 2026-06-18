<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/RootedOzoneFileSystem.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/RootedOzoneFileSystem.java

## Purpose
Minimal Hadoop 2-compatible rooted OFS implementation.

## Important APIs, types, and functions
Extends `BasicRootedOzoneFileSystem` and overrides `constructFileStatus` to use the Hadoop 2 `FileStatus` constructor without encrypted/EC fields.

## Control flow
All operations are inherited from the basic rooted filesystem; only status construction differs.

## State and persistence behavior
No additional state. Persistent state changes are inherited via Ozone adapter calls.

## Dependencies and integration points
Used by Hadoop 2 `RootedOzFs` and `FileSystem` resolution for `ofs://` paths.

## Risks and test signals
Expected metadata truncation for Hadoop 2 must not break path/list/status behavior. Tests should cover rooted status conversion, symlink-like bucket link targets where supported by base code, and basic operations on a Hadoop 2 classpath.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/RootedOzoneFileSystem.java -->
