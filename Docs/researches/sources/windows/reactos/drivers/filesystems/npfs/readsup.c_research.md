# File Research: sources/windows/reactos/drivers/filesystems/npfs/readsup.c

## Purpose
Implements copying data out of a pipe data queue for reads and peeks.

## Main Responsibilities
- `NpReadDataQueue`:
  - Reads from queued write entries into a caller buffer.
  - Supports peek mode without consuming entries.
  - Supports read-overflow behavior by forcing peek semantics.
  - Handles message-mode buffer overflow by returning `STATUS_BUFFER_OVERFLOW`.
  - Updates `QuotaInEntry`, `QuotaUsed`, and `ByteOffset` for consuming reads.
  - Transfers client security context from the data entry to the CCB.
  - Completes source write IRPs when data entries are fully consumed.
  - Calls `NpCompleteStalledWrites` after freeing quota.

## Important Interactions
- Called by `read.c` for real reads and `fsctrl.c` for peeks.
- Uses `NpGetNextRealDataQueueEntry` and `NpRemoveDataQueueEntry` from `datasup.c`.
- Uses `NpCopyClientContext` from `secursup.c`.

## Risks / Review Notes
- Exception handler around `RtlCopyMemory` contains `ASSERT(FALSE)` but does not set an error status; behavior after copy faults depends on build/assert handling.
- Message mode and overflow mode interact subtly: partial message reads surface `STATUS_BUFFER_OVERFLOW` while byte mode continues across entries.
