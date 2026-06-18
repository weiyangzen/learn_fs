# sources/user-network-fs/go-fuse/fs/inode_test.go

Purpose: unit test for `Inode.IsDir`.

Important test flow: iterates over standard `syscall.S_IF*` file type modes and asserts only `S_IFDIR` returns true.

State/dependencies: mutates a local `Inode.stableAttr.Mode`; no mount or external state.

Risks/test signals: narrow but useful guard that `IsDir` depends on file type bits rather than permissions. Broader inode behavior is covered in bridge, forget, loopback, and parent tests.
