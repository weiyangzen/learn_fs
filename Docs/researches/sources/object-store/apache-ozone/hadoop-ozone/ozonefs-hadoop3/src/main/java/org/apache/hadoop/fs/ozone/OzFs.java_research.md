<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop3/src/main/java/org/apache/hadoop/fs/ozone/OzFs.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop3/src/main/java/org/apache/hadoop/fs/ozone/OzFs.java

## Purpose
Hadoop 3 `AbstractFileSystem` adapter for `o3fs`.

## Important APIs, types, and functions
Extends `DelegateToFileSystem`, delegates to a new Hadoop 3 `OzoneFileSystem`, and uses the Ozone URI scheme. `finalize` closes the delegate.

## Control flow
FileContext operations route through `DelegateToFileSystem` to the underlying full filesystem.

## State and persistence behavior
State is held by the delegate and underlying filesystem. Durable mutations are delegated.

## Dependencies and integration points
Provides FileContext support for Hadoop 3 clients and participates in Hadoop filesystem service loading.

## Risks and test signals
The missing `getUriDefaultPort` override differs from Hadoop 2 but relies on delegate defaults. Tests should verify FileContext URI resolution and lifecycle behavior on Hadoop 3.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop3/src/main/java/org/apache/hadoop/fs/ozone/OzFs.java -->
