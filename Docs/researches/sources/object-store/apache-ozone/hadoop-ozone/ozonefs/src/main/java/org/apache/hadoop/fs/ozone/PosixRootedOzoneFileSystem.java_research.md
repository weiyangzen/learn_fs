<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/PosixRootedOzoneFileSystem.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/PosixRootedOzoneFileSystem.java

## Purpose
POSIX-oriented rooted OFS variant with double-create behavior.

## Important APIs, types, and functions
Extends `RootedOzoneFileSystem` and overrides the standard `create` method.

## Control flow
The method creates and closes a first stream, then creates again and returns the second stream.

## State and persistence behavior
Persists an initial empty key before the real write stream. All path translation and mutation semantics come from rooted OFS.

## Dependencies and integration points
Used for POSIX-like behavior with `ofs://` volume/bucket paths.

## Risks and test signals
Same double-create risks as `PosixOzoneFileSystem`, plus rooted path classification risks. Tests should cover rooted paths, overwrite behavior, metrics, and failure after the first close.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/PosixRootedOzoneFileSystem.java -->
