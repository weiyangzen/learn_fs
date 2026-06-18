# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/9fid.c

Manages Fossil 9P fid allocation, lookup, locking, reference counts, and cleanup.

Key behavior:
- Maintains a small free list of `Fid` objects and global counters.
- `fidGet()` looks up existing fids or creates new ones for `FidFCreate`, hashes them into the connection, and locks them for read or write.
- `fidPut()` decrements references and unlocks or frees invalidated fids.
- `fidClunk()` removes a fid from connection hash/list and frees it when references drop to zero.
- `fidClunkAll()` clunks every fid on a connection, used during version reset.

Important implementation details:
- `fidLock()` also takes the filesystem epoch read lock for established fids, preventing epoch changes during file operations.
- `FidOCreate` temporarily prevents accidental access during creation before the fid lock is acquired.
- `fidFree()` releases `File`, `DirBuf`, exclusive lock, auth RPC, `Fsys`, uid/uname/cuname, and locks.

Risks and invariants:
- `fidUnHash()` asserts refcount zero, so clunk paths require careful sequencing.
- Epoch lock pairing is embedded in fid lock/unlock, which makes all callers depend on this convention.
