<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/OzFs.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/OzFs.java

## Purpose
Main-module `AbstractFileSystem` adapter for `o3fs`.

## Important APIs, types, and functions
Extends `DelegateToFileSystem`, constructs a main-module `OzoneFileSystem`, uses the Ozone URI scheme, and closes the delegate in `finalize`.

## Control flow
FileContext calls delegate to the full bucket-scoped filesystem.

## State and persistence behavior
State is delegate-owned. Durable Ozone mutations are handled by the underlying filesystem.

## Dependencies and integration points
Exposes `o3fs` through Hadoop FileContext in the main non-shaded artifact.

## Risks and test signals
Same lifecycle risk as compatibility adapters due to `finalize`. FileContext contract tests should cover this class against the main artifact.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/OzFs.java -->
