# sources/storage-engines/foundationdb/fdbrpc/Net2FileSystem.cpp

`Net2FileSystem.cpp` implements the Net2 `IAsyncFileSystem` backend, selecting async file implementations and optional validation/chaos wrappers.

`Net2FileSystem::open()` checks allowed filesystem device IDs when configured, asserts exclusive/create consistency, chooses `AsyncFileCached` for buffered files, `AsyncFileKAIO` for Linux unbuffered AIO when enabled, or `Net2AsyncFile` otherwise, then optionally wraps the result in `AsyncFileWriteChecker` and `AsyncFileChaos`. Other APIs forward delete, last-write-time, rename, stop, and global filesystem registration. Linux-only KAIO test helpers exercise request-list timeout behavior.

Construction initializes `Net2AsyncFile`, initializes KAIO with the reactor eventfd when enabled, and validates configured filesystem paths as mount points by device ID. `open()` rejects files outside allowed devices before dispatching.

State includes `checkFileSystem` and sorted unique allowed device IDs. The module performs real filesystem operations through underlying async-file classes. Dependencies include async file backends, `AsioReactor`, platform helpers, Flow knobs, Boost.Asio setup, and global `INetwork::enFileSystem`.

Risks include platform-dependent KAIO availability, mount/device misconfiguration, wrapper-induced behavior changes, and large temporary files in tests. Test signals include `/fdbrpc/AsyncFileKAIO/RequestList` for KAIO timeouts and `Net2FileSystemTests.cpp` for general file semantics.
