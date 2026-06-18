## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_write.c

Purpose: implements file and deferred-xattr writes.

APIs and flow: `_9p_write` parses fid, offset, count, and data pointer; validates fid and negotiated `msize`; initializes op context; checks write access; writes into cached xattr content when `pfid->xattr` is active, otherwise prepares a one-iovec `fsal_io_arg` and calls `fsal_write`; records I/O stats; and returns `RWRITE` with actual bytes written.

State/dependencies: mutates file contents or fid xattr buffer. Xattr content is committed later on clunk. Depends on FSAL write, server stats, and write export permissions.

Risks/tests: xattr path increments offset by requested size rather than actual clipped size and has TODO gap detection. Test partial writes, offset gaps, msize limits, read-only exports, FSAL errors, xattr finalization, and stable-write expectations.
