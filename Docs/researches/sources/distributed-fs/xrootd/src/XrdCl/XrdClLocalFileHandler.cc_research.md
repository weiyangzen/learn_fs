# sources/distributed-fs/xrootd/src/XrdCl/XrdClLocalFileHandler.cc

## Purpose

This file implements `XrdCl::LocalFileHandler`, the local-file backend used when XRootD client requests target `localhost` or a local redirect. It translates XRootD open/read/write/stat/sync/truncate/vector I/O and fattr requests into POSIX/XrdSys local filesystem calls while preserving the normal asynchronous client callback model.

## Important APIs, Types, And Functions

The main exported methods are `Open`, `Close`, `Stat`, `Read`, `ReadV`, `Write`, `Sync`, `Truncate`, `VectorRead`, `VectorWrite`, `WriteV`, `SetXAttr`, `GetXAttr`, `DelXAttr`, `ListXAttr`, `QueueTask`, `MkdirPath`, and `ExecRequest`. `OpenImpl` performs URL validation, flag translation, file opening, stat parsing, and `OpenInfo` construction. `XAttrImpl` parses `kXR_fattr` request bodies and dispatches to the xattr methods.

The anonymous `AioCtx` class wraps POSIX `aiocb` for non-Apple async read/write/fsync. It chooses `SIGEV_SIGNAL` with `SIGUSR1` or `SIGEV_THREAD` based on the `AioSignal` environment setting, converts `aio_return`/`aio_error` results into `XRootDStatus` plus optional `ChunkInfo`, and queues a `LocalFileTask` through the `JobManager` unless the handler is synchronous.

## Control Flow

User-facing calls either complete synchronously and enqueue a `LocalFileTask`, or submit POSIX AIO and return immediately. `Open` calls `OpenImpl`; if the error is not local it returns directly, otherwise the status and response are delivered through `QueueTask`. `ExecRequest` decodes `ClientRequest::header.requestid` and routes protocol messages to the matching method, including virtual readv/writev cases carried through `MessageSendParams::chunkList`.

`OpenImpl` accepts only valid URLs with hostname `localhost`, maps XRootD flags to `O_CREAT`, `O_EXCL`, `O_WRONLY`, `O_RDWR`, `O_RDONLY`, and `O_TRUNC`, optionally creates parent directories, opens with `XrdSysFD_Open`, builds `StatInfo` from `fstat`, and records a single host entry for callbacks. Reads and writes use `aio_read`/`aio_write` on most platforms and `pread`/`pwrite` on Apple. Vector reads/writes iterate `ChunkList` or iovec arrays and return `VectorReadInfo` where appropriate.

## State And Persistence

The handler stores an open file descriptor `fd`, the current URL `pUrl`, and a host list `pHostList`. Persistent effects are real local filesystem effects: file creation, truncation, writes, fsync, and extended attribute changes. There is no recovery journal. Callback state is heap-owned by `XRootDStatus`, `AnyObject`, `HostList`, `LocalFileTask`, and `AioCtx` until the response handler consumes it.

## Dependencies And Integration Points

The file integrates with `DefaultEnv`, `PostMaster`, `JobManager`, `LocalFileTask`, `MessageUtils`, XRootD protocol request structures, `XrdSysFD_Open`, `XrdSysXAttr`, `XrdSysFAttr`, `XProtocol::mapError`, `StatInfo`, `OpenInfo`, `VectorReadInfo`, `ChunkInfo`, and `SyncResponseHandler`. It depends heavily on POSIX APIs: `open`, `close`, `fstat`, `pread`, `pwrite`, `readv`, `writev`, `preadv`, `pwritev`, `ftruncate`, `fsync`, and POSIX AIO.

## Risks

The AIO path uses a single process signal (`SIGUSR1`) when configured, which can conflict with embedding applications. `AioCtx` owns a raw `HostList*` allocated in its constructor and never visibly deletes it, so ownership depends on `LocalFileTask` after success/error queueing and can leak if `aio_read`/`aio_write` submission fails. `WriteV` uses a variable-length stack array, which is non-standard C++ and risks large stack allocation for large vectors. Several write paths treat non-negative short writes differently: Apple `Write` loops, `VectorWrite` does not. `XAttrImpl` parsing is sensitive to body length and NUL termination. `Close` does not reset `fd`, so repeated close or later operations on a closed descriptor are hazardous.

## Test Signals

Useful tests include local `root://localhost/...` open/read/write/stat/close flows, open with `kXR_mkpath`, failure on non-localhost URLs, sync handler and async handler callback delivery, short read and EOF behavior, vector read/write with multiple chunks, writev partial-write simulation, xattr get/set/list/delete including malformed fattr bodies, AIO signal and thread modes, Apple and non-Apple builds, and error mapping for permission, missing file, invalid path, and closed descriptor cases.
