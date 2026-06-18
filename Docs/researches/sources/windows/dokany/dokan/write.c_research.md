# File Research: sources/windows/dokany/dokan/write.c

Implements write dispatch, including a second driver round trip when the write payload is larger than the initial event batch.

Key behavior:
- `SendWriteRequest`:
  - uses pooled batch buffer for small contexts;
  - mallocs a larger `DOKAN_IO_BATCH` for large write event contexts;
  - sends `FSCTL_EVENT_WRITE` to fetch the full write payload from the driver.
- `DispatchWrite`:
  - initializes a no-output dispatch result;
  - if `RequestLength > 0`, retrieves a larger write context first;
  - maps `ERROR_OPERATION_ABORTED` to `STATUS_CANCELLED`;
  - maps other Win32 errors through `DokanNtStatusFromWin32`;
  - calls filesystem `WriteFile` with payload, length, offset, and file info;
  - on success, reports bytes written and updated `CurrentByteOffset`;
  - returns any temporary batch buffer to pool or frees it.

Role:
- Handles Dokan’s split write protocol where large write payloads are fetched on demand.
