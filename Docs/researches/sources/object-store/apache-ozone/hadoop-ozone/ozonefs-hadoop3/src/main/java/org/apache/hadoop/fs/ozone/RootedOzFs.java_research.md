<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop3/src/main/java/org/apache/hadoop/fs/ozone/RootedOzFs.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop3/src/main/java/org/apache/hadoop/fs/ozone/RootedOzFs.java

## Purpose
Hadoop 3 `AbstractFileSystem` adapter for rooted `ofs`.

## Important APIs, types, and functions
Extends `DelegateToFileSystem`, delegates to a new full `RootedOzoneFileSystem`, and uses scheme `ofs`. `finalize` closes the delegate.

## Control flow
All FileContext requests are delegated to the rooted filesystem.

## State and persistence behavior
State and persistence are owned by the delegate filesystem.

## Dependencies and integration points
Provides Hadoop 3 FileContext integration for OFS volume/bucket paths.

## Risks and test signals
Lifecycle finalization is nondeterministic. FileContext tests should cover initialization, URI handling, create/list/delete, and close behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop3/src/main/java/org/apache/hadoop/fs/ozone/RootedOzFs.java -->
