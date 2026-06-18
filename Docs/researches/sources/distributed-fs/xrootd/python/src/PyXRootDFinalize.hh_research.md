# sources/distributed-fs/xrootd/python/src/PyXRootDFinalize.hh

## Purpose
This header implements a module-level finalization hook for stopping XrdCl background threads from Python `atexit` handlers.

## Important APIs, Types, and Functions
`__XrdCl_Stop_Threads(PyObject *self, PyObject*)` releases the GIL, calls `XrdCl::DefaultEnv::GetPostMaster()->Stop()`, reacquires the GIL, and returns `None`.

## Control Flow
The function is called explicitly from Python shutdown logic. It blocks outside the GIL while XrdCl's postmaster stops job manager, task manager, and poller threads.

## State and Persistence
It mutates process-global XrdCl thread/runtime state. No persistence.

## Dependencies and Integration Points
Depends on Python C API, `XrdClDefaultEnv`, and `XrdClPostMaster`. Registered as `__XrdCl_Stop_Threads` in the extension module.

## Risks and Test Signals
Shutdown ordering is sensitive; async response handlers also guard against interpreter finalization. Tests should verify the hook can be called repeatedly or at least safely during teardown, does not deadlock, and leaves no XrdCl worker threads after interpreter exit.
