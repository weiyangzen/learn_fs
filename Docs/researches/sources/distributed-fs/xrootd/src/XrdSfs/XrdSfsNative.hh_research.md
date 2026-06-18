# sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsNative.hh

## Purpose
Declares the native POSIX SFS implementation classes used by `XrdSfsNative.cc`.

## Important APIs, Types, And Functions
- `XrdSfsNativeDirectory : XrdSfsDirectory` declares directory open, iteration, close, and `FName()`.
- `XrdSfsNativeFile : XrdSfsFile` declares file open/close, descriptor fctl, mmap/compression stubs, preread no-op, scalar/vector read/write, sync, stat, and truncate.
- `XrdSfsNative : XrdSfsFileSystem` declares object factories and namespace operations plus static `Mkpath()` and `Emsg()`.

## Control Flow
Factories allocate concrete native directory/file objects. Inline stubs return success for preread, zero stats, default prepare, no compression, and mode-stat forwarding. The implementation file supplies all real POSIX calls.

## State And Persistence
Directory state consists of `DIR *`, EOF flag, path string, and a portable `dirent` buffer. File state consists of descriptor `oh` and path string. Filesystem state consists of static `eDest` for logging. Persistent behavior is delegated to POSIX storage.

## Dependencies And Integration Points
Depends on `XrdSfsInterface.hh`, `dirent.h`, and `XrdSysError`/`XrdSysLogger` forward declarations. This header is used by the server-native SFS module and potentially by wrappers that need native-specific declarations.

## Risks And Edge Cases
Inline methods mirror implementation risks: `getMmap()` does not clear `*Addr`; `getCXinfo()` returns assignment value `0` instead of an SFS return code; destructor descriptor handling depends on `oh` truthiness. API signatures use `XrdSecClientName` aliases from the security interface, so type compatibility must be preserved.

## Test Signals
Compile native SFS against the current interface, instantiate file/directory factories, verify inline mode-stat forwarding and stub return values, and run destructor/close tests for unopened and descriptor-zero cases.
