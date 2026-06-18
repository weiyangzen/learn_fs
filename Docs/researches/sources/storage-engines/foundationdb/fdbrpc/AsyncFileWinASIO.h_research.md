# sources/storage-engines/foundationdb/fdbrpc/AsyncFileWinASIO.h

## Purpose
`AsyncFileWinASIO.h` provides the Windows `IAsyncFile` backend using `boost::asio::windows::random_access_handle` over a `CreateFile` handle opened with no buffering and overlapped flags.

## Important APIs, Types, and Functions
The main type is `AsyncFileWinASIO`. Important methods include `open`, `deleteFile`, `lastWriteTime`, `read`, `write`, `truncate`, `sync`, `size`, `renameFile`, `debugFD`, and callback helpers `onReadReady`/`onWriteReady`. The implementation stores the ASIO random-access handle, open flags, and original filename.

## Control Flow
`open` handles atomic-create by opening `filename + ".part"`, maps Flow flags to `CreateFile` access/share/creation options, and wraps the handle in the ASIO file object. `read` checks the current file size, returns zero at EOF, and issues `async_read_some_at`. `write` issues `boost::asio::async_write_at` and validates the exact byte count. `truncate` uses `SetFilePointerEx` plus `SetEndOfFile`. `sync` calls `FlushFileBuffers` and, for atomic create, moves the `.part` file to the target.

## State and Persistence Behavior
Persistent state is the Windows file handle and open flags. Writes become durable only when `sync` flushes the handle. Atomic create state is stored in the flags until the first `sync`, which performs the move and clears `OPEN_ATOMIC_WRITE_AND_CREATE`.

## Dependencies and Integration Points
The file is compiled only under `WIN32`, aliases `Net2AsyncFile` to `AsyncFileWinASIO`, and depends on Windows APIs plus Boost.Asio. It integrates with Flow's `IAsyncFile` abstraction and platform helpers `deleteFile`/`renameFile`.

## Risks and Edge Cases
The file comments note that the implementation is not fully asynchronous: truncate and sync are synchronous and can block the network thread. `getClassName` contains a spelling typo (`AsnycFileWinASIO`). `MoveFile` during atomic sync does not use write-through semantics and its result is not checked. No-buffering on Windows imposes alignment constraints, but this wrapper does not assert alignment the way KAIO does. `read` calls `size().get()` inline, so size errors propagate synchronously.

## Test Signals
Signals are Windows builds and file-system integration tests that use unbuffered I/O. This subset has no Windows-specific unit test for short writes, atomic rename failure, alignment enforcement, or blocking sync/truncate behavior.
