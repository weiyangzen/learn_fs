# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpFactory.hh

## Purpose
`XrdClHttpFactory.hh` declares the final `Factory` class implementing `XrdCl::PlugInFactory` for HTTP-backed file and filesystem plugin instances.

## Important APIs and Types
The class overrides `CreateFile` and `CreateFileSystem`, exposes static `GetHeaderTimeoutWithDefault`, and provides `Produce` for queueing `CurlOperation` work. Private helpers include `Initialize`, `SetupX509`, `Monitor`, and static `Shutdown`. Static members hold shared queue/log/thread/shutdown state and defaults such as `m_poll_threads`.

## Control Flow
The header defines a lazy initialization model: object creation calls `Initialize`, which creates shared runtime infrastructure on first use. `shutdown_s` invokes `Shutdown` when the library unloads.

## State and Persistence
The factory state is process-wide rather than per factory instance. It owns a shared handler queue, monitor thread, initialization guard, stats location, start time, and shutdown signaling primitives.

## Dependencies and Integration Points
It depends on XrdCl plugin interfaces plus C++ threading primitives. It forward-declares `CurlOperation`, `CurlWorker`, and `HandlerQueue`, keeping operation details out of the public factory header.

## Risks and Test Signals
The static lifecycle makes ordering important when the shared library is unloaded. Tests should check that `CreateFile` and `CreateFileSystem` return null if initialization fails, `Produce` is not called before queue setup, and shutdown is idempotent.
