# sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppSymlinkTest.h

Purpose: basic typed tests for symlink creation, target reading, and removal in root and nested directories.

Important APIs/types/functions: `FsppSymlinkTest`, `CreateSymlink`, `LoadSymlink`, `Symlink::target`, `Node::remove`, and typed GoogleTest registration.

Control flow: creates symlinks with absolute and relative target strings, reloads them through typed symlink access, and compares `target()` results. Remove tests verify both generic and symlink-specific load paths disappear.

State and persistence behavior: symlink target text is persisted as node data; removal updates directory entries and makes the node unavailable through `Device`.

Dependencies and integration points: uses `FileSystemTest`, `boost::none`, fspp `Symlink`, and concrete typed fixtures.

Risks and test signals: validates basic symlink functionality but does not cover invalid targets, overwrite semantics, directory timestamp side effects, or permission-related behavior. Timestamp coverage is delegated to the paired timestamp test file.
