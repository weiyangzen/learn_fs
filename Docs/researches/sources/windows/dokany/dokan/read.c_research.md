# File Research: sources/windows/dokany/dokan/read.c

Implements `DispatchRead`, the read request dispatcher.

Key behavior:
- Allocates an output buffer sized to the requested read length using `CreateDispatchCommon` with extra memory pool enabled.
- Calls `DokanOperations->ReadFile` with filename, output buffer, requested length, offset, and `DOKAN_FILE_INFO`.
- Defaults status to `STATUS_NOT_IMPLEMENTED`.
- On success:
  - zero bytes read becomes `STATUS_END_OF_FILE`;
  - nonzero bytes set `BufferLength`;
  - updates `CurrentByteOffset`.
- Completes through `EventCompletion`.

Role:
- Bridges kernel read events to user filesystem read callbacks and packages returned bytes for the driver.
