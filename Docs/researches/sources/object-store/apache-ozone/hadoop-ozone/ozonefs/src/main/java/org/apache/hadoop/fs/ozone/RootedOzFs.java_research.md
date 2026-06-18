<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/RootedOzFs.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/RootedOzFs.java

## Purpose
Main-module `AbstractFileSystem` adapter for rooted `ofs`.

## Important APIs, types, and functions
Extends `DelegateToFileSystem`, constructs `RootedOzoneFileSystem`, uses `ofs` scheme, and closes the delegate in `finalize`.

## Control flow
FileContext APIs delegate to the rooted filesystem.

## State and persistence behavior
State is delegate-owned; persistence is handled by underlying OFS.

## Dependencies and integration points
Provides FileContext integration for rooted Ozone paths in the main artifact.

## Risks and test signals
Lifecycle and URI-resolution risks mirror other `RootedOzFs` variants. FileContext tests should cover rooted operations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/RootedOzFs.java -->
