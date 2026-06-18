# sources/user-network-fs/nfs-utils/support/nfs/rmtab.c

Purpose: read/write helpers for the NFS remote mount table (`rmtab`) that records client, path, and mount count.

Important APIs: `setrmtabent()`, `fsetrmtabent()`, `getrmtabent()`, `fgetrmtabent()`, `putrmtabent()`, `fputrmtabent()`, `endrmtabent()`, `fendrmtabent()`, `rewindrmtabent()`, and `frewindrmtabent()`. Global `struct state_paths rmtab` supplies the default path.

Control flow: reader parses one `host:path:count` line, converts semicolons back to colons in the client field for IPv6 presentation addresses, defaults missing count to 1, and returns a static `struct rmtabent`. Writer optionally seeks to a supplied position, converts client colons to semicolons, and emits count as fixed-width hex.

State and persistence: global `FILE *rmfp` is the default open table. The durable state is the rmtab file. Static buffers/entries are reused per read.

Dependencies and integration: used by mountd/export utilities tracking remote mounts. Depends on `nfslib.h` and `xlog`.

Risks: colon replacement is lossy for unusual host names containing semicolons. No file locking is performed here. Static buffer and global handle are not reentrant. Path values containing colons are not escaped.

Test signals: IPv4/hostname and IPv6 client round-trip, missing count, malformed line logging/errno, positioned overwrite, long client rejection, and concurrent writers if external locking is expected.
