<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/test/java/org/apache/hadoop/fs/ozone/TestOFSPath.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/test/java/org/apache/hadoop/fs/ozone/TestOFSPath.java

## Purpose
Unit tests for `OFSPath` parsing semantics used heavily by rooted filesystem operations.

## Important APIs, types, and functions
Tests construct `OFSPath` from strings with volume, bucket, key, spaces, trailing slashes, empty input, authority, and `/tmp` mount syntax. Assertions check authority, volume, bucket, mount, key name, non-key path, mount detection, and string rendering.

## Control flow
Each test creates one or more `OFSPath` instances against an `OzoneConfiguration` and asserts parsed components. The mount test uses `OFSPath.getTempMountBucketNameOfCurrentUser` to derive the expected current-user temporary bucket name.

## State and persistence behavior
No persistent state is used. Parsing depends on current user for `/tmp` mount bucket naming.

## Dependencies and integration points
These signals support `BasicRootedOzoneFileSystem` rename/delete/trash/symlink logic because that class relies on accurate `OFSPath` classification and key/non-key split.

## Risks and test signals
Trailing slash behavior is contract-heavy: bucket paths normalize differently than key directory paths. Missing cases include snapshot paths, link buckets, invalid names, root-only paths, and authority edge cases with malformed ports.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/test/java/org/apache/hadoop/fs/ozone/TestOFSPath.java -->
