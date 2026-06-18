# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCallBack.hh

## Purpose
Declares `XrdOucCallBack`, a serial-use helper for managing `XrdOucErrInfo` asynchronous callbacks safely enough for common XRootD framework use.

## Important APIs, Types, And Functions
The class derives from `XrdOucEICB`. Public methods are `Allowed`, `Cancel`, `Init`, and `Reply`. `Next` is a public link field for pools/lists. Private overrides `Done` and `Same` satisfy the callback interface; `Done` posts the semaphore used by `Reply`, while `Same` always returns false.

## Control Flow
Users check `Allowed`, call `Init`, return/emit the wait-for-callback response, and later call `Reply` or `Cancel`. The destructor calls `Cancel` when a callback is still armed.

## State And Persistence
The class holds only in-memory callback handoff state: semaphore, opaque callback argument, original callback pointer, and copied 64-byte user id. It has no ownership of external callback objects beyond the temporary pointer.

## Dependencies And Integration Points
Includes `XrdOucErrInfo.hh` and `XrdSysPthread.hh`. The class is a utility layer over the `XrdOucEICB` callback contract used by plugins and request handlers.

## Risks And Test Signals
The header explicitly warns that the object is not MT-safe and that failing to effect a callback response after `Init` can hang future users. Compile coverage should verify virtual signatures, while runtime tests should exercise allowed/not-allowed paths, destructor cancel, and reply with optional path tracing.
