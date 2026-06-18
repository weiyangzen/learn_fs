# sources/distributed-fs/xrootd/src/XrdCl/XrdClPlugInInterface.hh

## Purpose

This header defines the client-side plugin ABI for replacing or extending `XrdCl::File` and `XrdCl::FileSystem` behavior. It is intentionally broad: plugin implementations may override file open/read/write/control operations, filesystem metadata operations, extended attributes, and factory creation for URL-specific clients.

## Important APIs, Types, And Functions

`FilePlugIn` is the file-object interface. It mirrors `File` methods such as `Open`, `OpenUsingTemplate`, `Close`, `Stat`, `Read`, `PgRead`, `Write`, `PgWrite`, `Sync`, `Truncate`, `PreRead`, `VectorRead`, `VectorWrite`, `WriteV`, `Fcntl`, `Visa`, `IsOpen`, property accessors, `ExportTemplate`, and `Clone`. Most default implementations return `XRootDStatus(stError, errNotImplemented)`; `PreRead` returns success, `IsOpen` returns false, and template export returns an empty unique pointer.

`FileSystemPlugIn` mirrors `FileSystem` methods including `Locate`, `DeepLocate`, `Mv`, `Query`, path `Truncate`, `Rm`, `MkDir`, `RmDir`, `ChMod`, `Ping`, `Stat`, `StatVFS`, `Protocol`, `DirList`, `SendInfo`, `Prepare`, xattr operations, and property accessors. `PlugInFactory` creates `FilePlugIn` and `FileSystemPlugIn` instances for a URL.

## Control Flow

The header contains interface defaults only; dispatch happens in `File`, `FileSystem`, and `PlugInManager`. A consumer asks a factory to create a plugin for a URL, then forwards public client operations to the returned object. Implementations can be partial because unsupported methods fail with `errNotImplemented`.

## State And Persistence Behavior

The base classes keep no state. Implementations may maintain open handles, caches, clone templates, or backend-specific configuration. Ownership is raw-pointer based at the factory boundary: callers must know who owns returned plugin instances, while `PlugInManager` owns factories.

## Dependencies And Integration Points

The file includes `XrdClFile.hh`, `XrdClFileSystem.hh`, and `XrdClOptional.hh`, tying the plugin ABI to public file and filesystem request/response types such as `OpenFlags`, `Access`, `ResponseHandler`, `Buffer`, `ChunkList`, `TractList`, `QueryCode`, `DirListFlags`, `PrepareFlags`, `xattr_t`, `ExportedFileTemplate`, and `CloneLocations`.

## Risks And Edge Cases

The ABI uses many raw pointers and asynchronous handlers, so plugins must document ownership and callback behavior carefully. Default success for `PreRead` can hide missing prefetch support. Some methods accept file descriptors, buffers, or iovecs and must respect lifetime constraints after returning. Factory-created objects need ABI-compatible allocation/deallocation across shared libraries.

## Test Signals

Tests should register a fake plugin and verify that `File`/`FileSystem` route all supported operations, unsupported operations return `errNotImplemented`, properties round-trip, clone/template paths reject incompatible templates, and async response handlers are invoked exactly once.
