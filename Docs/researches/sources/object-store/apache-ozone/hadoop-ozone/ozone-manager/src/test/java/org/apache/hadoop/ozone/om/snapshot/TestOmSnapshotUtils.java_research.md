# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshotUtils.java

## Purpose
`TestOmSnapshotUtils` is a focused unit test for `OmSnapshotUtils.linkFiles(File source, File target)`. It verifies that the snapshot utility can copy a directory tree structure into a target location using hard links for files, which is central to snapshot checkpoint creation and local metadata reuse.

## Important APIs, Types, and Functions
- `OmSnapshotUtils.linkFiles(tree1, tree2)` is the API under test.
- `Files.write`, `Files.walk`, and `Path::toString` construct and compare source and target directory trees.
- `IOUtils.getINode(Path)` validates hard-link identity rather than content-only equality.
- JUnit `@TempDir` provides an isolated filesystem workspace.

## Control Flow
The test builds `tree1` with two directories and one file, asserts that target `tree2` and the expected linked file do not exist, invokes `linkFiles`, and then asserts that the target tree exists. It compares source and target inode values for `f1` and `tree2/dir1/f1`, then walks both trees and normalizes `tree1` paths to the expected `tree2` paths.

## State and Persistence Behavior
This test directly exercises filesystem persistence. The key invariant is that `linkFiles` creates hard links, not byte-for-byte copied files, so the inode of the linked file must match the source. Directory structure is persisted under the temporary target root and must mirror the source.

## Dependencies and Integration Points
The test depends on filesystem hard-link support in the local platform. It integrates with the snapshot utility layer used by OM snapshot/checkpoint code and with `hdds` inode helpers.

## Risks and Edge Cases
- The test covers a nested tree and one file but not empty directories beyond `dir2`, existing destination trees, symlink handling, permission failures, or cross-filesystem hard-link errors.
- The inode assertion may be platform-sensitive if the test environment does not support hard links.

## Test Signals
Passing assertions signal that `linkFiles` creates the target tree, preserves the full path set, and makes file entries share inodes with the source.
