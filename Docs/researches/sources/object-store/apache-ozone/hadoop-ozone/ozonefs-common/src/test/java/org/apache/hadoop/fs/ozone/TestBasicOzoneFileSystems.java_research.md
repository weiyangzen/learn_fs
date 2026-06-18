<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/test/java/org/apache/hadoop/fs/ozone/TestBasicOzoneFileSystems.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/test/java/org/apache/hadoop/fs/ozone/TestBasicOzoneFileSystems.java

## Purpose
Parameterized unit tests for shared behavior in `BasicOzoneFileSystem` and `BasicRootedOzoneFileSystem`.

## Important APIs, types, and functions
The `data` method supplies both filesystem implementations. Tests cover default block size from `OZONE_SCM_BLOCK_SIZE`, customized block size parsing, pseudo-POSIX symlink support, and snapshot return path construction. Mockito spies and mocked adapters isolate snapshot creation.

## Control flow
Each parameterized test sets an `OzoneConfiguration` or spies the filesystem, performs a single API call, and asserts common or implementation-specific results. Snapshot tests mock adapter `createSnapshot` to return a fixed name and compare the returned path under the bucket snapshot root.

## State and persistence behavior
No real Ozone state is used. State is local configuration and mocked adapter behavior.

## Dependencies and integration points
Exercises Hadoop `FileSystem` defaults, Ozone configuration storage-size parsing, `OM_SNAPSHOT_INDICATOR`, and both `o3fs` and `ofs` path formats.

## Risks and test signals
The tests guard compatibility-sensitive return values, especially snapshot path trimming and rooted-only symlink support. They do not cover actual OM snapshot creation, link bucket behavior, or initialized filesystem URIs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/test/java/org/apache/hadoop/fs/ozone/TestBasicOzoneFileSystems.java -->
