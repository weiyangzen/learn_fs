## sources/user-network-fs/go-fuse/fuse/attr_linux.go

Purpose: Linux-specific conversion from syscall `Stat_t` and `unix.Statx_t` to FUSE protocol structs.

Important APIs/types/functions: `Attr.FromStat` maps inode, size, blocks, timestamps, mode, link count, owner, device, and block size. `Statx.FromStatx` maps statx timestamps, mask, attributes, device numbers, and ownership.

Control flow: direct field assignment from kernel syscall structs into FUSE structs.

State and persistence: stateless conversion; no storage.

Dependencies and integration: used by Linux loopback, statx dispatch, and tests that compare mounted and backing metadata.

Risks and test signals: Linux struct layout and field semantics are platform-specific. `statx_linux_test.go` is the direct signal for statx conversion fidelity.
