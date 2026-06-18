## sources/user-network-fs/go-fuse/fuse/attr_unix.go

Purpose: non-Linux Unix conversion from `syscall.Stat_t` to FUSE `Attr`.

Important APIs/types/functions: `Attr.FromStat` maps inode, size, blocks, `Atimespec`/`Mtimespec`/`Ctimespec`, mode, nlink, uid, gid, rdev, and block size.

Control flow: build-tag-selected direct conversion for Darwin/FreeBSD-style stat fields.

State and persistence: no state; mutates the destination attribute object.

Dependencies and integration: supports loopback and nodefs/pathfs metadata on non-Linux platforms.

Risks and test signals: platform field names differ from Linux. Errors appear as wrong stat output, permissions, or cache behavior on non-Linux CI.
