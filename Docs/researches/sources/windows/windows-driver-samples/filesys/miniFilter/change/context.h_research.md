# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/change/context.h

## Purpose

Defines context structures and public context helper prototypes for the `change` minifilter sample.

## Data Structures

- `CG_TRANSACTION_CONTEXT` stores:
  - Referenced `PKTRANSACTION`.
  - `Enlisted` flag.
  - `ListDrained` flag.
  - `ScListHead`, the list of file contexts participating in the transaction.
  - Nonpaged `PFAST_MUTEX` protecting the list.
- `CG_FILE_REFERENCE` is a union supporting both 64-bit file IDs and 128-bit ReFS file IDs.
- `CG_FILE_CONTEXT` stores:
  - File ID.
  - Non-transactional `Dirty` flag.
  - Transaction-local `TxDirty` flag.
  - Current transaction context pointer.
  - Embedded transaction-list entry.

## Constants

- `CG_FILE_CONTEXT_TAG` and `CG_TRANSACTION_CONTEXT_TAG` identify context allocations.
- `CG_TRANSACTION_CONTEXT_SIZE` and `CG_FILE_CONTEXT_SIZE` wrap `sizeof()` for registration/allocation.

## API Surface

- `CgFindOrCreateFileContext(PFLT_CALLBACK_DATA Cbd, PCG_FILE_CONTEXT *FileContext)`.
- `CgFindOrCreateTransactionContext(PCFLT_RELATED_OBJECTS FltObjects, PCG_TRANSACTION_CONTEXT *TransactionContext)`.

## Dependencies And Usage

- Used by `change.c` for dirty tracking and transaction enlistment.
- Implemented by `context.c`.
- Requires WDK Filter Manager and KTM-related types from `fltKernel.h`.

## Risks And Invariants

- `ListInTransaction` is valid only while the file context is linked into one transaction context list.
- `TxContext` and list membership must be updated together with the transaction-context mutex and interlocked pointer operations used by `change.c`.
- `ListDrained` prevents new file contexts from being inserted into a transaction context after KTM outcome processing has drained it.
