# sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsInterface.hh

## Purpose
Defines the core Standard File System plugin ABI for XRootD. It specifies open flags, return codes, request structures, directory/file object interfaces, filesystem-wide operations, and plugin entry-point typedefs.

## Important APIs, Types, And Functions
- Open flags such as `SFS_O_RDONLY`, `SFS_O_CREAT`, `SFS_O_POSC`, `SFS_O_RAWIO`, `SFS_O_REPLICA`, and `SFS_O_MKPTH`.
- Return codes `SFS_OK`, `SFS_ERROR`, `SFS_REDIRECT`, `SFS_STALL`, `SFS_STARTED`, `SFS_DATA`, and `SFS_DATAVEC`.
- `XrdSfsDirectory` declares directory `open()`, `nextEntry()`, `close()`, `FName()`, and optional `autoStat()`.
- `XrdSfsFile` declares file open/close, fctl, mmap, page I/O, scalar/vector read/write, sendfile hook, stat, sync, truncate, compression info, and optional exchange-buffer setup.
- `XrdSfsFileSystem` declares object factories and namespace/filesystem operations such as checksum, chmod, exists, FAttr, FSctl/fsctl, stats, gpFile, mkdir, prepare, remove, rename, stat, and truncate.
- `XrdSfsFileSystem2_t` and `XrdSfsFileSystem_t` define new and legacy plugin factory signatures.

## Control Flow
The server obtains an `XrdSfsFileSystem` implementation through a plugin entry point, creates per-request file/directory objects through `newFile()` and `newDir()`, and invokes virtual methods using the return-code and `XrdOucErrInfo` contract. Optional capabilities are discovered through `Features()` and through default virtual implementations. Wrapping guidance in the header defines how wrappers should share the same `XrdOucErrInfo` across chains.

## State And Persistence
`XrdSfsDirectory` and `XrdSfsFile` own or borrow an `XrdOucErrInfo` reference depending on constructor choice. `XrdSfsFileSystem` owns a protected `FeatureSet`. Actual namespace, file data, caching, checkpoints, and transfer persistence are delegated to implementations.

## Dependencies And Integration Points
Depends on XRootD OUC range/IO/error types, `XrdSfsGPFile`, and system stat types. It is the ABI boundary used by native SFS, SSI SFS wrappers, authorization/cache layers, and third-party filesystem plugins.

## Risks And Edge Cases
- ABI stability is critical because plugins compile against this header.
- Return-code semantics overload `XrdOucErrInfo.code` for errors, redirects, stalls, data lengths, and async estimates.
- Wrapper constructors require careful error-object propagation; mixed ownership can cause stale pointers or duplicate deletes.
- Some flags intentionally share numeric ranges for different contexts, so callers must mask appropriately.

## Test Signals
ABI/compile tests for plugins, wrapper-chain tests verifying a shared error object, return-code contract tests for redirect/stall/data responses, feature negotiation tests, and compatibility tests for both plugin factory signatures are important.
