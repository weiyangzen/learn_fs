## sources/user-network-fs/go-fuse/fuse/nodefs/memnode_test.go

Purpose: tests for deprecated nodefs memory filesystem behavior.

Important APIs/types/functions: tests construct `NewMemNodeFSRoot`, mount it through nodefs, create/read/write/rename/remove files and directories, and verify visible results.

Control flow: each test mounts the memnode root into a temp mountpoint, performs filesystem operations through the kernel, and unmounts.

State and persistence: in-memory tree plus temporary backing files created by `memnode.go`.

Dependencies and integration: validates `memNode`, `FileSystemConnector`, and raw FUSE dispatch working together.

Risks and test signals: detects regressions in basic namespace mutation, file content persistence during mount lifetime, and cleanup.
