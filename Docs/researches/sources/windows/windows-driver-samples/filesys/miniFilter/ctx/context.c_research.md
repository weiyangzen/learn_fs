# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/ctx/context.c

## Purpose
Implements creation, lookup, attachment, replacement, and name-update logic for the `ctx` sample’s file, stream, and stream-handle contexts.

## Key Functions
- `CtxFindOrCreateFileContext`
  - Attempts `FltGetFileContext`.
  - If missing and creation is requested, allocates a file context and attaches it with `FltSetFileContext`.
  - Handles `STATUS_FLT_CONTEXT_ALREADY_DEFINED` races by releasing the new context and returning the existing one from `oldFileContext`.

- `CtxCreateFileContext`
  - Allocates `FLT_FILE_CONTEXT` from `PagedPool`.
  - Copies the supplied file name into `fileContext->FileName`.

- `CtxFindOrCreateStreamContext`
  - Attempts `FltGetStreamContext`.
  - If missing and requested, allocates and attaches a stream context.
  - Handles concurrent attach races by using `oldStreamContext`.

- `CtxCreateStreamContext`
  - Allocates and zeroes a stream context.
  - Allocates an `ERESOURCE` with `CtxAllocateResource`.
  - Initializes it with `ExInitializeResourceLite`.

- `CtxUpdateNameInStreamContext`
  - Frees any existing stream-context file name.
  - Allocates and copies the supplied name.
  - Caller is responsible for synchronization.

- `CtxCreateOrReplaceStreamHandleContext`
  - Always allocates a new stream-handle context.
  - Attaches it with either `FLT_SET_CONTEXT_REPLACE_IF_EXISTS` or `FLT_SET_CONTEXT_KEEP_IF_EXISTS`.
  - Releases replaced contexts when needed.
  - Handles already-defined races when replacement is not requested.

- `CtxCreateStreamHandleContext`
  - Allocates and zeroes a stream-handle context.
  - Allocates and initializes its `ERESOURCE`.

- `CtxUpdateNameInStreamHandleContext`
  - Frees any existing handle-context name.
  - Allocates and copies the supplied name.
  - Caller is responsible for synchronization.

## Concurrency and Lifetime Pattern
The file consistently follows Filter Manager context rules:
- `FltAllocateContext` returns a referenced context.
- Successful `FltSet*Context` creates an object-held reference.
- The caller retains and later releases its own returned reference.
- If a set loses a race to another thread, the new context is released and the existing context is returned.

## Notable Detail
`CtxCreateFileContext` assigns `*FileContext = fileContext` and returns `STATUS_SUCCESS` even if `CtxAllocateUnicodeString` fails. That means a file context may be returned without a populated `FileName` buffer if allocation fails. Stream and stream-handle context creation paths return allocation failures more directly for their resource allocations.

## Dependencies
- Uses global `Globals.Filter`.
- Uses tags and structures from `CtxStruc.h`.
- Uses resource and string helpers from `CtxProc.h` / `support.c`.

## Research Notes
This is the central context mechanics file for the sample. It is useful as a compact reference for correct `FltGet*Context` / `FltSet*Context` race handling.
