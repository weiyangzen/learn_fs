<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/OzoneFileSystem.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/OzoneFileSystem.java

## Purpose
Minimal Hadoop 2-compatible `o3fs` filesystem implementation.

## Important APIs, types, and functions
Extends `BasicOzoneFileSystem` and overrides `constructFileStatus` to call the Hadoop 2 `FileStatus` constructor, which lacks newer encryption and erasure-coded arguments.

## Control flow
All filesystem behavior is inherited. File status conversion maps fields from `FileStatusAdapter` to the Hadoop 2 constructor.

## State and persistence behavior
No additional state is introduced. Persistent behavior is inherited from the basic filesystem and adapter.

## Dependencies and integration points
Used by Hadoop 2 `OzFs` and `FileSystem` resolution. It is intentionally missing Hadoop 3 interfaces such as `StreamCapabilities`, `LeaseRecoverable`, and `KeyProviderTokenIssuer`.

## Risks and test signals
Metadata loss for encryption/EC flags is expected because Hadoop 2 lacks those constructor fields. Tests should verify status construction remains compatible on a Hadoop 2 classpath and basic filesystem operations still work.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/OzoneFileSystem.java -->
