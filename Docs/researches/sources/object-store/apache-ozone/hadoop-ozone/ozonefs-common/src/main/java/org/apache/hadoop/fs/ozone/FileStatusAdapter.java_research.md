<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/FileStatusAdapter.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/FileStatusAdapter.java

## Purpose
Compatibility data carrier for file status metadata that can be converted into Hadoop 2 or Hadoop 3 `FileStatus` constructors by platform-specific filesystem classes.

## Important APIs, types, and functions
The final class stores length, disk consumed, path, directory flag, replication, block size, modification/access times, permission bits, owner, group, symlink, block locations, encryption flag, and EC flag. It exposes getters, `isFile`, `isDir`, `getBlockLocations`, and a diagnostic `toString`.

## Control flow
Construction copies the supplied `BlockLocation[]` into an internal list. Consumers call getters and filesystem-specific `constructFileStatus` methods to build Hadoop-native status objects.

## State and persistence behavior
Instances are immutable except the internal list reference is private and only exposed as copied arrays. It represents live OM metadata but does not persist anything itself.

## Dependencies and integration points
Produced by `OzoneClientAdapter.listStatus` and `getFileStatus`, then consumed by `BasicRootedOzoneFileSystem`, `BasicOzoneFileSystem`, and Hadoop 2/3 status constructors. It carries block locations for `LocatedFileStatus` conversion and encryption/EC flags where supported.

## Risks and test signals
Constructor parameter ordering is long and error-prone. Risks include dropping block locations, losing symlink/encryption/EC metadata in Hadoop 2 conversions, or stale disk consumed values affecting content summaries. Listing, getFileStatus, and content summary tests should verify every field that downstream contracts rely on.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/FileStatusAdapter.java -->
