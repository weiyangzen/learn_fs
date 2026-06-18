# File Research: sources/os/bsd/openbsd-src/sys/sys/namei.h

Defines pathname lookup state, component-name metadata, name cache entries, namei flags, and unveil path-check integration.

Key contents:
- `struct nameidata` captures pathname, dirfd, segment type, starting/root directories, pledge/unveil requirements, result vnodes, symlink/path traversal state, and nested `struct componentname`.
- Namei operations: `LOOKUP`, `CREATE`, `DELETE`, `RENAME`.
- Lookup modifiers: `LOCKLEAF`, `LOCKPARENT`, `WANTPARENT`, `NOCACHE`, `FOLLOW`.
- Operational flags including `NOCROSSMOUNT`, `RDONLY`, `HASBUF`, `SAVENAME`, `SAVESTART`, `MAKEENTRY`, `ISLASTCN`, `ISSYMLINK`, `REALPATH`, `BYPASSUNVEIL`, `KERNELPATH`, and zoneinfo/localtime symlink policy bits.
- `struct namecache` for vnode/name lookup cache.
- Name cache statistics and sysctl names.
- Unveil flags: read, write, create, exec, userset, pledge-open.

Key APIs:
- `ndinitat`, `NDINITAT`, `NDINIT`.
- `namei`, `vfs_lookup`, `vfs_relookup`.
- `cache_lookup`, `cache_enter`, `cache_purge`, `cache_revlookup`, `cache_purgevfs`.
- Unveil helpers for add, vnode removal, lookup, relative start, component/final checks.

Risk notes:
- This is a critical VFS/security boundary: pledge, unveil, symlink, mount-crossing, realpath, and parent-locking flags interact in one structure.
