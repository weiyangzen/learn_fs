# sources/user-network-fs/go-fuse/fs/abort_test.go

Purpose: verifies Linux FUSE connection abort propagates cancellation to a blocked filesystem operation.

Important types/functions: `hangingRootNode` implements `OpendirHandle`, closes `openCalled`, waits for `ctx.Done`, records `canceled`, and returns `EINTR`. `TestAbort` mounts the node, derives the FUSE connection ID from mount device, starts a blocking directory open, writes to `/sys/fs/fuse/connections/<id>/abort`, expects the open to fail, unmounts, and asserts cancellation was observed.

State/dependencies: Linux-only, requires `/sys/fs/fuse/connections` access and a real FUSE mount.

Risks/test signals: high-value coverage for abort/cancel path; can be environment-sensitive due to kernel permissions and timing. It explicitly skips non-Linux.
