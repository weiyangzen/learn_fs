<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/RootedOzFs.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/RootedOzFs.java

## Purpose
Hadoop 2 `AbstractFileSystem` adapter for rooted `ofs`.

## Important APIs, types, and functions
Extends `DelegateToFileSystem`, constructs a Hadoop 2-compatible `RootedOzoneFileSystem`, uses scheme `ofs`, returns default port `-1`, and closes the delegate in `finalize`.

## Control flow
FileContext calls delegate to the rooted filesystem instance.

## State and persistence behavior
Only delegate state is held locally; durable changes occur through the underlying filesystem.

## Dependencies and integration points
Exposes OFS to Hadoop 2 FileContext users, including volume/bucket path semantics supplied by `BasicRootedOzoneFileSystem`.

## Risks and test signals
Lifecycle close through finalization is nondeterministic. Tests should verify FileContext resolution and rooted path operations on Hadoop 2.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/RootedOzFs.java -->
