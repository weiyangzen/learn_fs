# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/change/context.c

## Purpose

Implements file and transaction context allocation, lookup, initialization, cleanup, and file-ID extraction for the transaction-aware `change` minifilter sample.

## Public And Internal APIs

- Context registration: `ContextRegistration[]`.
- File context APIs: `CgFindOrCreateFileContext()`, local `CgCreateFileContext()`, `CgFileContextCleanup()`.
- Transaction context APIs: `CgFindOrCreateTransactionContext()`, `CgTransactionContextCleanup()`.
- File identity helper: `CgGetFileId()`.

## Context Registration

- Registers `FLT_FILE_CONTEXT` with `CgFileContextCleanup()`, size `CG_FILE_CONTEXT_SIZE`, tag `CG_FILE_CONTEXT_TAG`.
- Registers `FLT_TRANSACTION_CONTEXT` with `CgTransactionContextCleanup()`, size `CG_TRANSACTION_CONTEXT_SIZE`, tag `CG_TRANSACTION_CONTEXT_TAG`.

## File Context Flow

- `CgFindOrCreateFileContext()` first attempts `FltGetFileContext()`.
- On `STATUS_NOT_FOUND`, it queries a file ID using `CgGetFileId()`, allocates a file context from paged pool, zeroes it, stores the file ID, and attempts `FltSetFileContext(..., FLT_SET_CONTEXT_KEEP_IF_EXISTS, ...)`.
- If another thread won the race and already set a context, it releases the newly allocated context and returns the existing `oldFileContext`.
- `CgFileContextCleanup()` asserts the file is not still linked to a transaction context and logs file ID plus dirty state.

## Transaction Context Flow

- `CgFindOrCreateTransactionContext()` first attempts `FltGetTransactionContext()`.
- On `STATUS_NOT_FOUND`, it allocates a nonpaged fast mutex separately, allocates a paged transaction context, zeroes it, stores and references the KTM transaction object, initializes the file-context list and mutex, then sets the transaction context with `FLT_SET_CONTEXT_KEEP_IF_EXISTS`.
- If a race finds an already-defined transaction context, it releases the new context and returns the old one.
- `CgTransactionContextCleanup()` frees the separately allocated fast mutex and dereferences the KTM transaction object.

## File ID Handling

- `CgGetFileId()` calls `FltGetFileSystemType()`.
- For ReFS, it queries `FileIdInformation` and copies the 128-bit file ID.
- For other file systems, it queries `FileInternalInformation`, stores the 64-bit index number, and zeroes the upper 64 bits.

## Dependencies

- Filter Manager context APIs: `FltAllocateContext`, `FltGetFileContext`, `FltSetFileContext`, `FltGetTransactionContext`, `FltSetTransactionContext`, `FltReleaseContext`, `FltQueryInformationFile`, `FltGetFileSystemType`.
- Kernel object references: `ObReferenceObject`, `ObDereferenceObject`.
- Allocation helpers from `utility.h`: `CgAllocateMutex()`, `CgFreeMutex()`.

## Risks And Invariants

- Transaction-context mutex is allocated from nonpaged pool because fast mutex storage must be resident.
- File context cleanup asserts `TxContext == NULL`; transaction cleanup/list drain must clear all file links before file context teardown.
- Races in context creation are handled through `FLT_SET_CONTEXT_KEEP_IF_EXISTS`; returned existing contexts carry references that callers must release.
- `CgFindOrCreateTransactionContext()` references the KTM transaction object and relies on cleanup to dereference it exactly once.
- File identity is normalized to a 128-bit union so NTFS-style and ReFS-style IDs can be logged through common storage.
