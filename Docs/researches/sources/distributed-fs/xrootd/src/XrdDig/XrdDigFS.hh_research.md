## sources/distributed-fs/xrootd/src/XrdDig/XrdDigFS.hh

### Purpose
This header declares the digFS directory, file, and filesystem classes implementing XRootD's SFS interface.

### Important APIs, Types, and Functions
- `XrdDigDirectory` derives from `XrdSfsDirectory` and exposes `open`, `nextEntry`, `close`, `FName`, and `autoStat`.
- `XrdDigFile` derives from `XrdSfsFile` and exposes read-only `open`, `close`, `fctl`, `read`, `readv`, AIO read, `stat`, and no-op/rejected write-style operations.
- `XrdDigFS` derives from `XrdSfsFileSystem`, allocates directory/file objects, rejects mutating methods, implements `exists`, `fsctl`, `stat`, `getVersion`, and common `Emsg`/`Validate`.

### Control Flow
The SFS server obtains an `XrdDigFS`, then calls `newDir` or `newFile` to handle individual operations. Most mutators inline-call `Reject`, making the filesystem explicitly read-only at the interface level.

### State and Persistence
Directory objects keep `DIR *`, a mapped filename, optional autostat buffer, directory fd, EOF/base/proc flags, and a fixed union buffer for directory entries or synthesized root entries. File objects keep an fd, mapped filename, and proc flag. Filesystem objects are stateless.

### Dependencies and Integration Points
The header includes `XrdSfsInterface.hh`, POSIX `dirent`/types, and is implemented by `XrdDigFS.cc`. It is part of `XrdServer` through `XrdDig/CMakeLists.txt`.

### Risks and Edge Cases
The fixed `dirent_full` storage needs to be large enough for directory names plus proc symlink tags on all supported platforms. The inline no-op writes return `SFS_OK`, while filesystem-level mutators reject; callers must not interpret file write support from these methods. Destructor cleanup calls virtual-like `close` methods during destruction but the methods are local concrete implementations.

### Test Signals
Compile and ABI tests should confirm SFS signature compatibility. Runtime tests should cover object lifecycle, repeated open protection, destructor cleanup of open handles, autostat behavior, and read-only method behavior.
