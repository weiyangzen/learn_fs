# File Research: sources/windows/dokany/dokan/flush.c

Implements `DispatchFlush`, the user-mode event handler for flush buffer requests.

Key behavior:
- Validates/logs the flush target path via `CheckFileName`.
- Initializes the dispatch result with `CreateDispatchCommon` and no output payload.
- Calls `DokanOperations->FlushFileBuffers` if the filesystem supplied it.
- Treats `STATUS_NOT_IMPLEMENTED` as successful flush completion.
- Converts other non-success callback statuses to `STATUS_NOT_SUPPORTED`.
- Completes the request with `EventCompletion`.

Role in architecture:
- Bridges Dokan driver flush requests to the filesystem’s `FlushFileBuffers` callback.
- Keeps flush optional, matching common filesystem behavior where no explicit flush hook is required.
