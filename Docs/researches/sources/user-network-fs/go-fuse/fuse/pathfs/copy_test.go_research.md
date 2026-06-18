## sources/user-network-fs/go-fuse/fuse/pathfs/copy_test.go

Purpose: tests basic `CopyFile` behavior between loopback pathfs instances.

Important APIs/types/functions: `TestCopyFile` creates two temp dirs, wraps them with `NewLoopbackFileSystem`, writes source content, calls `CopyFile`, then verifies destination content. It repeats in reverse to confirm overwrite.

Control flow: file data is written to one backing dir, copied through pathfs APIs, read from the other backing dir, then copied back.

State and persistence: uses real temp-directory files as durable test data.

Dependencies and integration: validates pathfs loopback plus nodefs file read/write behavior indirectly.

Risks and test signals: covers normal copy and overwrite only; not permissions, partial writes, large files, or error cleanup.
