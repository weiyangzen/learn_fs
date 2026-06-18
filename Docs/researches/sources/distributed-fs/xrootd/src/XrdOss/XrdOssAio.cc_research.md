# sources/distributed-fs/xrootd/src/XrdOss/XrdOssAio.cc

## Purpose

`XrdOssAio.cc` implements asynchronous read/write/fsync support for the default OSS file object using POSIX AIO when available, with synchronous fallback completion when AIO is disabled or unavailable.

## Important APIs, Types, and Functions

Implemented methods are `XrdOssFile::Fsync(XrdSfsAio*)`, `Read(XrdSfsAio*)`, `Write(XrdSfsAio*)`, and `XrdOssSys::AioInit()`. Helper/thread functions include `XrdOssAioWait`, local signal constants `OSS_AIO_READ_DONE` and `OSS_AIO_WRITE_DONE`, and fallback signal-handler shims `XrdOssAioRSH`, `XrdOssAioWSH`, and `sigwaitinfo` when needed. Static state includes `XrdOssFile::AioFailure` and `XrdOssSys::AioAllOk`.

## Control Flow

On systems with POSIX AIO and successful `AioInit()`, file async methods fill the `aiocb` file descriptor, completion signal, and trace identity, then call `aio_read`, `aio_write`, or `aio_fsync`. AIO wait threads synchronously wait for read/write signals, obtain `aio_error` and `aio_return`, store `aiop->Result`, and invoke `doneRead()` or `doneWrite()`. If AIO is unsupported, disabled, returns `EAGAIN`/`ENOSYS`, or initialization fails, the methods execute the synchronous file operation and immediately call the completion routine.

## State and Persistence Behavior

AIO state is process-global: `AioAllOk` enables native AIO, wait threads run for process lifetime, and failure count throttles logging. Each request owns its `XrdSfsAio` control block and receives result/completion. No durable persistence exists.

## Dependencies and Integration Points

The code depends on platform AIO/signal APIs, `XrdSfsAio`, `XrdSysThread`, `XrdSysPlatform`, and OSS trace/error globals. It integrates with `XrdOssFile` methods from `XrdOssApi.cc` for fallback synchronous I/O.

## Risks and Edge Cases

Platform behavior is conditional and explicitly disables macOS POSIX AIO. Signal selection uses real-time signals when available, so process-wide signal masking must be correct. Fallback `Fsync(XrdSfsAio*)` assigns `-errno` after `Fsync()` even though `Fsync()` already returns negative errno, which should be reviewed. Busy-waiting while `aio_error` returns `EINPROGRESS` may spin briefly.

## Test Signals

Tests should cover builds with and without `_POSIX_ASYNCHRONOUS_IO`, initialization failure, fallback completion, native read/write completion, fsync completion, unexpected signal logging, AIO `EAGAIN` fallback, and result sign conventions.
