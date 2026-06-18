# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/defrag/TestInodeMetadataRocksDBCheckpoint.java

## Purpose
`TestInodeMetadataRocksDBCheckpoint` validates `InodeMetadataRocksDBCheckpoint`, which reads hard-link metadata and creates hard links for RocksDB checkpoint files, including paths prefixed with `om.db/`.

## Important APIs, Types, and Functions
- `InodeMetadataRocksDBCheckpoint(Path)` and `InodeMetadataRocksDBCheckpoint(Path, boolean deleteSourceFiles)` are constructed.
- A `hardLinkFile` in the checkpoint directory maps target paths to source paths separated by tabs.
- `IOUtils.getINode(Path)` verifies hard-link identity.

## Control Flow
The first test creates `source.sst`, writes a hardlink metadata file with one `om.db/target1.sst` target and one root-level `target2.sst` target, constructs the checkpoint wrapper, and asserts both targets exist and share the source inode. The second test constructs with `deleteSourceFiles=false`, verifies the source file remains, and checks that the `om.db/target.sst` link is created.

## State and Persistence Behavior
The tested behavior is filesystem-persistent: target links are created under the checkpoint directory, parent directories such as `om.db` must be created when needed, and source deletion is controlled by constructor argument/version mode.

## Dependencies and Integration Points
This test supports snapshot defrag/checkpoint code that stores inode metadata for SST hard links. It ensures compatibility with the newer `om.db/` path prefix and older source-preserving format.

## Risks and Edge Cases
- Hard-link behavior is filesystem-dependent.
- The tests do not cover malformed metadata rows, missing source files, duplicate targets, or delete-source true assertions.

## Test Signals
Passing means inode metadata checkpoint reconstruction creates expected hard links, handles `om.db/` target prefixes, and can preserve source files for v1-style metadata.
