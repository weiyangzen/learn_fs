# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/ctx/operations.c

## Purpose
Implements the I/O operation callbacks for the `ctx` minifilter sample. It demonstrates how file, stream, and stream-handle contexts are created, updated, counted, and queried across create, cleanup, close, and rename operations.

## Operation Flow
- `CtxPreCreate`
  - Trace-only pre-create callback.
  - Always returns `FLT_PREOP_SUCCESS_WITH_CALLBACK` so `CtxPostCreate` can attach contexts after successful open.

- `CtxPostCreate`
  - Ignores failed creates.
  - Queries normalized file name with `FltGetFileNameInformation`.
  - Finds or creates a stream context, increments `CreateCount`, and updates the stream name under exclusive resource protection.
  - Creates or replaces a stream-handle context and updates its name under exclusive protection.
  - Builds a file name excluding the stream-name suffix and finds or creates a file context.
  - Releases all acquired contexts and name information before return.
  - Does not modify the underlying create status if its own context work fails.

- `CtxPreCleanup`
  - Retrieves existing stream context only.
  - Increments `CleanupCount` under exclusive resource protection.
  - Ignores errors and returns `FLT_PREOP_SUCCESS_NO_CALLBACK`.

- `CtxPreClose`
  - Retrieves existing stream context only.
  - Increments `CloseCount` under exclusive resource protection.
  - Ignores errors and returns `FLT_PREOP_SUCCESS_NO_CALLBACK`.

- `CtxPreSetInfo`
  - Only requests a post-operation callback for `FileRenameInformation` and `FileRenameInformationEx`.
  - Uses `FLT_PREOP_SYNCHRONIZE` so the post-operation callback can run in the initiating thread at a pageable IRQL.

- `CtxPostSetInfo`
  - Ignores failed set-information operations.
  - Retrieves instance context for logging.
  - Queries the normalized post-rename name.
  - Retrieves existing stream context and updates its name under exclusive protection.
  - Creates or replaces stream-handle context and updates its name.
  - Retrieves, but does not modify, existing file context. This matches the sample’s design where file context name is immutable after creation.

## Synchronization
Mutable context fields are protected with the resource helpers from `CtxProc.h`:
- stream `FileName` and counters
- stream-handle `FileName`

File context does not have a lock because its name is intended to be immutable.

## Error Handling
Failures in context bookkeeping are traced but generally do not fail already-successful file-system operations. This is intentional sample behavior: context logging should not alter the successful result from the underlying file system.

## Research Notes
The file demonstrates the semantic difference between stream, stream-handle, and file contexts:
- Stream context follows the file stream across opens and records aggregate counters.
- Stream-handle context is replaced for each successful open or rename update.
- File context captures a stable file-level name without stream suffix and is not renamed in place.
