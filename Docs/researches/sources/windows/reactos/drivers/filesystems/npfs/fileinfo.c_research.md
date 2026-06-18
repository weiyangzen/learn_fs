# File Research: sources/windows/reactos/drivers/filesystems/npfs/fileinfo.c

## Purpose
Implements query/set file information for NPFS pipe file objects. Most information is synthetic because named pipes do not map to normal disk files.

## Main Responsibilities
- `NpFsdSetInformation` dispatches set-info requests under the exclusive VCB lock.
- `NpSetBasicInfo` accepts basic-info changes but performs no work.
- `NpSetPipeInfo` changes per-end read mode and completion mode:
  - Rejects message read mode for byte-stream pipes.
  - Rejects switching to complete-operation mode in some busy queue states.
  - Notifies directory watchers through `NpCheckForNotify`.
- `NpFsdQueryInformation` dispatches query-info requests under the shared VCB lock.
- Query helpers provide:
  - `FileBasicInformation`: normal attributes.
  - `FileStandardInformation`: quota allocation and readable byte count.
  - `FileNameInformation`: root or pipe full name.
  - `FilePositionInformation`: readable byte count as current offset.
  - `FilePipeLocalInformation`: pipe type, configuration, quotas, state, end, available bytes.
  - `FilePipeInformation`: read/completion modes.
  - `FileInternalInformation` and `FileEaInformation`: zeroed placeholders.
  - `FileAllInformation`: composed from several helper outputs.

## Important Interactions
- Uses `NpDecodeFileObject` to distinguish CCB/root handles.
- Reads data queue state directly to compute available data and quota.
- Mode updates affect `read.c`, `write.c`, `readsup.c`, `writesup.c`, and `fsctrl.c`.

## Risks / Review Notes
- `NpQueryPipeLocalInfo` has an asymmetric client-end quota calculation: client `WriteQuotaAvailable` uses `OutQueue->Quota - InQueue->QuotaUsed`. Given client writes target the inbound queue, this deserves review.
- Length handling subtracts structure sizes from an unsigned `ULONG`; callers must provide valid buffer lengths or underflow risk depends on I/O manager validation.
- `FileAllInformation` intentionally omits or skips several standard substructures by subtracting access/mode/alignment sizes rather than filling them.
