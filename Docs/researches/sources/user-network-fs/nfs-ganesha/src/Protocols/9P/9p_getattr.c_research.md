## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_getattr.c

Purpose: implements `TGETATTR`, translating FSAL attributes into 9P2000.L stat fields.

APIs and flow: `_9p_getattr` parses fid and request mask, gets `ATTRS_NFS3` attributes through `obj_ops->getattrs`, computes the returned valid mask and selected fields, maps FSAL object type to POSIX mode bits, fills qid, ownership, size, block, and timestamp fields, and returns `RGETATTR`.

State/dependencies: read-only operation over fid/object/export state. It depends on FSAL attr preparation/release and uses export filesystem id for `rdev`, while birth time, generation, and data version are stubbed as zero.

Risks/tests: test per-bit mask behavior, type-to-mode mapping, timestamp precision, attr release on error, and unsupported/stubbed attributes expected by Linux 9p clients.
