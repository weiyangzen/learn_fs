# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/context.h

Kernel-private context model for the AV minifilter. It defines infection-state enums, pool tags, state transition macros, stream/transaction/section/instance context layouts, and prototypes for context creation/enumeration helpers.

Key definitions:
- `AV_FILE_INFECTED_STATE`: `AvFileUnknown`, `AvFileInfected`, `AvFileNotInfected`, `AvFileModified`, `AvFileScanning`.
- State macros distinguish normal state from transaction-isolated `TxState`.
- `IS_FILE_NEED_SCAN` requires scanning when a non-transacted file is modified or a transacted file’s `TxState` is modified.
- `AV_TRANSACTION_CONTEXT` stores the transaction pointer, list of associated stream contexts, synchronization resource, and flags for enlisted/list-drained state.
- `AV_STREAMHANDLE_CONTEXT` stores per-handle flags, currently `AV_FLAG_PREFETCH`.
- `AV_STREAM_CONTEXT` stores flags, file ID, transaction context pointer, transaction-list entry, scan synchronization event, normal and transaction infection states, and CSVFS revision numbers.
- `AV_SECTION_CONTEXT` stores data-scan section handle/object, abort state, file size, conflict-cancelability, and backpointer to scan context.
- `AV_INSTANCE_CONTEXT` stores volume/instance pointers, filesystem type, volatile file-state cache table, cache resource, and CSV hidden-volume flag.

Declared interfaces:
- Transaction context: `AvFindOrCreateTransactionContext`.
- Section, stream-handle, and stream context creation.
- Instance enumeration/free helpers.

Dependencies:
- Uses types from Filter Manager, KTM, Windows lists/events/resources, and `AV_FILE_REFERENCE` from `utility.h`.

Research notes:
- The state macros use `InterlockedExchange`, making state transitions atomic but not full compound-state protocols.
- CSVFS revision fields are part of the generic stream context so core scan logic can update them after CSV-specific checks.
