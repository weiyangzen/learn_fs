# sources/distributed-fs/xrootd/src/XrdCl/XrdClFileSystem.hh

## Purpose
`XrdClFileSystem.hh` declares the public `XrdCl::FileSystem` API and the protocol-facing enum wrappers used by XRootD clients. It is the main user-facing filesystem control surface for locating files, moving/removing paths, querying server state, listing directories, preparing files, manipulating extended attributes, and managing filesystem properties.

## Important APIs, Types, And Functions
The header defines `QueryCode::Code`, `OpenFlags::Flags`, `Access::Mode`, `MkDirFlags::Flags`, `DirListFlags::Flags`, and `PrepareFlags::Flags`, mostly mapping directly to `kXR_*` protocol constants. `XRDOUC_ENUM_OPERATORS` enables flag composition for the relevant enum types. `FileSystem` exposes paired async and sync overloads for `Locate`, `DeepLocate`, `Mv`, `Query`, `Truncate`, `Rm`, `MkDir`, `RmDir`, `ChMod`, `Ping`, `Stat`, `StatVFS`, `Protocol`, `DirList`, `SendCache`, `SendInfo`, `Prepare`, and xattr methods. Async overloads take `ResponseHandler *`; sync overloads either return status only or fill caller-owned response pointers/references.

Private members include `SendSet`, template `XAttrOperationImpl`, lock helpers used by fork handling, and raw pointers `pImpl` and `pPlugIn`. Copy construction and assignment are declared private to keep instances non-copyable.

## Control Flow
The header does not implement request flow, but its overload shape establishes the implementation contract: callback methods return immediately with submission status, while sync methods block until a protocol response is available. The private `SendSet` consolidates `SendCache` and `SendInfo`, and `XAttrOperationImpl` consolidates all filesystem-level xattr commands.

## State And Persistence Behavior
`FileSystem` hides mutable state in `FileSystemImpl`; the ABI note says the raw pointer remains until ABI can change to shared ownership. `pPlugIn` redirects behavior to a plugin when available. There is no on-disk state; properties such as `FollowRedirects` and `LastURL` are process-local.

## Dependencies And Integration Points
The API depends on `URL`, `XRootDStatus`, XRootD response model classes, protocol constants, `XrdSysPthread`, and `MessageSendParams`. `ForkHandler` and `AssignLBHandler` are friends so they can lock or adjust internal routing state. `FileSystemPlugIn` can replace built-in behavior for URL-specific protocols.

## Risks And Test Signals
Tests should verify ABI-facing overloads remain source-compatible, enum values match protocol constants, default timeouts of `0` are honored, sync response ownership is documented and respected, and `SetProperty`/`GetProperty` behavior matches implementation. Because xattr methods use vector references rather than response pointers, tests should include empty, single, and bulk xattr cases.
