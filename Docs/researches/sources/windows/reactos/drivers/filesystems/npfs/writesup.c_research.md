# File Research: sources/windows/reactos/drivers/filesystems/npfs/writesup.c

## Purpose
Implements delivery of write data into queued read IRPs.

## Main Responsibilities
- `NpWriteDataQueue`:
  - Iterates queued read entries while data remains.
  - Handles internal read-overflow FSCTL reads specially.
  - Copies write data into read IRP buffers or allocated intermediate buffers.
  - Captures client security context once per write and stores it on the CCB.
  - Completes read IRPs with success or `STATUS_BUFFER_OVERFLOW` depending on message/byte mode.
  - Reports remaining bytes via `BytesNotWritten`.
  - Returns `STATUS_MORE_PROCESSING_REQUIRED` when data remains and must be buffered/queued.

## Important Interactions
- Called by `write.c` and `fsctrl.c` transceive.
- Uses `NpGetNextRealDataQueueEntry` and `NpRemoveDataQueueEntry`.
- Security context capture uses `NpGetClientSecurityContext`.

## Risks / Review Notes
- Internal overflow read handling depends on FSCTL major/function fields of queued read IRPs.
- Allocated buffer ownership is transferred to IRP flags with `IRP_DEALLOCATE_BUFFER | IRP_BUFFERED_IO | IRP_INPUT_OPERATION`.
- Sparse or zero-length message behavior is represented by `MoreProcessing`, which is easy to misread.
