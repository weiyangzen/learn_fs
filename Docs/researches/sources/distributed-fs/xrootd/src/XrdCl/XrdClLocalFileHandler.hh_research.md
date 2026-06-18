# sources/distributed-fs/xrootd/src/XrdCl/XrdClLocalFileHandler.hh

## Purpose

This header declares `XrdCl::LocalFileHandler`, the client-side adapter that exposes the usual XRootD file operation surface for local files. It lets the rest of XrdCl execute protocol-shaped requests without knowing whether the target is remote or a local filesystem object.

## Important APIs, Types, And Functions

The public API mirrors file operations: `Open`, local redirect `Open(const URL*, const Message*, AnyObject*&)`, `Close`, `Stat`, `Read`, `ReadV`, `Write`, `Sync`, `Truncate`, `VectorRead`, `VectorWrite`, `WriteV`, `Fcntl`, `Visa`, xattr methods, `QueueTask`, `MkdirPath`, `SetHostList`, `GetHostList`, and `ExecRequest`. Private helpers are `OpenImpl` and `XAttrImpl`.

The class owns `int fd`, `std::string pUrl`, and `HostList pHostList`. It accepts `ResponseHandler` callbacks and `MessageSendParams`, and returns `XRootDStatus` immediately while actual operation results are usually delivered later.

## Control Flow

Callers may invoke the typed methods directly, or `ExecRequest` may translate an incoming XRootD `Message` into a typed method. Most methods report completion through `QueueTask`, which creates or bypasses a `LocalFileTask` depending on the response handler type.

The overload accepting `URL` plus `Message` exists for local redirect handling: it extracts open flags and mode from a `ClientOpenRequest` and calls the same open implementation used by normal `Open`.

## State And Persistence

The header defines the state contract: one handler instance represents one local open file descriptor and a host list used for callback metadata. Local filesystem persistence is implemented in the `.cc` file, but the API exposes mutating operations such as write, truncate, sync, and xattr modification.

## Dependencies And Integration Points

The declaration depends on `XrdClJobManager.hh`, `XrdClLocalFileTask.hh`, `XrdClDefaultEnv.hh`, `XrdClLog.hh`, `sys/uio.h`, XrdCl response types, `ChunkList`, `xattr_t`, `Message`, `MessageSendParams`, `URL`, and `ResponseHandler`. It is consumed by message routing and postmaster code that needs to service local redirects.

## Risks

The class is not marked thread-safe, yet shared descriptor state could be used from asynchronous callbacks. Timeout parameters are present on most methods but local operations mostly ignore them after dispatch. `Fcntl` and `Visa` are declared in the same surface but implemented as unsupported, which callers must handle. The API accepts raw pointers for handlers, buffers, chunk lists, and response objects, so ownership discipline is critical.

## Test Signals

Header-level signals are build coverage across platforms, ABI compatibility for all declared overloads, successful compilation of code paths that use `ExecRequest`, and tests that direct file API calls and protocol-message calls produce equivalent statuses/responses for open, read, write, stat, sync, truncate, vector I/O, and xattrs.
