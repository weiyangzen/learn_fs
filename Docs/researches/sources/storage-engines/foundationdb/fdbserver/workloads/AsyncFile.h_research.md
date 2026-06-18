# sources/storage-engines/foundationdb/fdbserver/workloads/AsyncFile.h

## Purpose
`AsyncFile.h` declares shared async file workload utilities and implements the common `openFile` actor. It centralizes file opening, temporary file creation, aligned buffer requirements, optional file prefill, and cleanup semantics for async file workloads.

## Important APIs, Types, and Functions
- `RandomByteGenerator`: deterministic random filler for optional random file contents.
- `AsyncFileBuffer`: reference-counted buffer wrapper with optional 4 KiB alignment.
- `AsyncFileHandle`: reference-counted file wrapper with path and temporary cleanup flag.
- `AsyncFileWorkload`: base `TestWorkload` with unbuffered/uncached IO options, `fillRandom`, enablement, duration, handle, size, and path.
- `AsyncFileWorkload::openFile`: actor that replaces existing handles, chooses a temporary name when needed, adjusts flags, opens the file, optionally truncates/fills it, and stores the handle.

## Control Flow
`openFile` clears any existing file reference and briefly waits, then generates `asyncfile.<UID>` if no path is provided. It forces read-write/create flags for new files and read-write flags for fill operations, applies `OPEN_UNBUFFERED`/`OPEN_UNCACHED`, opens through `IAsyncFileSystem`, and records or updates `fileHandle`. If creation or fill is requested, it aligns the target size upward to a page boundary and writes 256 KiB chunks, pipelining one write behind.

## State and Persistence Behavior
The actor may create a temporary file later deleted by `AsyncFileHandle`. Fill can truncate existing files and rounds target size to 4 KiB. The generated path is saved in `self->path`, allowing later reopens. `openFile` receives desired size as an argument; callers generally read actual `file->size()` afterward to update `fileSize`.

## Dependencies and Integration Points
The header depends on tester workload infrastructure and `flow/IAsyncFile.h`. It is included by `AsyncFileCorrectness`, `AsyncFileRead`, and `AsyncFileWrite`, and integrates directly with `IAsyncFileSystem::open`, `IAsyncFile::write`, `truncate`, and `sync`.

## Risks
Outstanding uncancellable IO can outlive the fixed 0.1-second handle-clear delay, so workloads must use `holdWhile` correctly. Fill size alignment may surprise tests expecting exact configured sizes. Extending from `oldSize & ~(chunkSize - 1)` can rewrite from a previous chunk boundary. Open failure logs `TestFailure` and rethrows. Unbuffered IO relies on callers using aligned buffers, offsets, and sizes.

## Test Signals
Open failures emit `TraceEvent(SevError, "TestFailure").detail("Reason", "Could not open file")`. File-building progress prints per GiB. Success is indirect through async file workload setup and metrics.
