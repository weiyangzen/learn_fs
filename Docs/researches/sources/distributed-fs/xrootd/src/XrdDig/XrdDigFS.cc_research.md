## sources/distributed-fs/xrootd/src/XrdDig/XrdDigFS.cc

### Purpose
This file implements the read-only digFS `XrdSfsFileSystem`, directory, and file objects. It exposes selected server administrative files through XRootD's SFS interface, with authorization and path mapping delegated to `XrdDigConfig`.

### Important APIs, Types, and Functions
- `XrdDigGetFS(...)` is the plugin entry point used by xrootd configuration to initialize and return a singleton `XrdDigFS`.
- `XrdDigDirectory::open`, `nextEntry`, and `close` implement authorized directory listing, including synthesized root entries and Linux `/proc` symlink tagging.
- `XrdDigFile::open`, `read`, `readv`, AIO read wrapper, `stat`, `fctl`, and `close` implement read-only file access.
- `XrdDigFS::exists`, `fsctl`, `stat`, `getVersion`, `Validate`, `Reject`, and `Emsg` provide filesystem-level operations and common error formatting.
- `XrdDigUFS` wraps POSIX `open`, `close`, `stat`, `lstat`, and `fstat` for easier replacement or isolation.

### Control Flow
`XrdDigGetFS` sets the global error route, configures the global `Config`, and returns a static filesystem on success. Directory opens either synthesize the dig root listing through `Config.GenAccess` or validate/map/open a real directory. `nextEntry` loops over directory entries, optionally autostats them, normalizes modes to read-only, and, for Linux proc paths, appends `" -> target"` text for symlinks unless listing the proc root.

File open rejects write/create modes, validates and maps the path, applies Linux `/proc` restrictions by requiring a regular non-`/mem` target, opens read-only, and verifies the descriptor is a regular file. Reads use `pread`; `readv` loops over individual `pread` calls and treats short reads as an error. Filesystem-level stat handles the dig root specially and otherwise delegates to `Config.GenPath` then POSIX `stat`.

### State and Persistence
The filesystem is read-only; mutation methods return `EROFS`. Runtime state lives in each directory/file object: open DIR/file descriptor, allocated real filename, proc/base flags, autostat buffer pointer, and EOF state. Global state is `eDest` and `Config`. No persistent state is written by this file.

### Dependencies and Integration Points
The file depends on XrdSfs interfaces, XrdSec identity, XrdSys logging, XrdVersion, XrdOuc error info, and POSIX filesystem APIs. Xrootd's config path calls `XrdDigGetFS`; SFS calls allocate `XrdDigDirectory` and `XrdDigFile` via `newDir`/`newFile`.

### Risks and Edge Cases
`exists` appears to call `Statfn(path, ...)` on the supplied logical path rather than a mapped real path, unlike `stat` and `open`; this may be intentional for local-prefixed paths but is worth testing. In `getMmap`, `if (Addr) Addr = 0` does not clear `*Addr`. `XrdDigFile::open` stores negative errno values in `oh` and then passes them through `Emsg`, which normalizes sign. Directory symlink tagging writes into `dirent` name storage and depends on buffer layout. `readv` treats any short read as `ESPIPE`, which may be harsh near EOF. Proc validation and `/mem` substring blocking need security regression coverage.

### Test Signals
Expected tests include successful plugin initialization, denied startup on config failure, root listing filtered by auth, read-only rejection for all mutating operations, stat/open/read/readv success for exported files, locate `fsctl`, `/proc` symlink display and open rejection, logical path validation, and error-info contents for common failures.
