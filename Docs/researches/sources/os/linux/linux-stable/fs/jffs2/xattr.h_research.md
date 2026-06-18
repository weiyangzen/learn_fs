# File Research: sources/os/linux/linux-stable/fs/jffs2/xattr.h

Defines the in-memory JFFS2 xattr model and public subsystem API.

Key structures:
- `struct jffs2_xattr_datum` represents one deduplicated xattr name/value payload, with raw node pointer, prefix, xid/version, CRC, hash key, cached name/value pointers, and refcount.
- `struct jffs2_xattr_ref` represents an inode-to-xdatum association, using unions so scan/build time stores raw inode/xid values and runtime stores `ic`/`xd` pointers.
- `XREF_DELETE_MARKER` marks deleted xrefs in the low bit of `xseqno`.

Feature gates:
- Under `CONFIG_JFFS2_FS_XATTR`, declares lifecycle, mount-build, inode cleanup, GC, get/set, listxattr, and handler symbols.
- Without xattr support, most APIs compile to no-op stubs and `jffs2_verify_xattr()` returns complete.
- Security xattrs are separately gated by `CONFIG_JFFS2_FS_SECURITY`.

Risk notes:
- The struct layout assumes first fields line up with raw-node ownership conventions used elsewhere in JFFS2.
- The scan/runtime union fields require callers to respect subsystem build phases.
