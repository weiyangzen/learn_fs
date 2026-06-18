# File Research: sources/windows/dokany/dokan/access.c

User-mode helper for retrieving the Windows access token of the process/thread that issued a Dokan create request.

Key responsibilities:
- Implements `DokanOpenRequestorToken(PDOKAN_FILE_INFO)`.
- Validates that `DOKAN_FILE_INFO.DokanContext` points to a valid `DOKAN_IO_EVENT` with an event context and instance.
- Restricts token retrieval to `IRP_MJ_CREATE` callbacks.
- Builds a small `EVENT_INFORMATION` request carrying the event serial number.
- Sends `FSCTL_GET_ACCESS_TOKEN` to the per-mount raw device name and returns the driver-provided token handle.

Important behavior:
- Returns `INVALID_HANDLE_VALUE` and sets `ERROR_INVALID_PARAMETER` for invalid context or non-create events.
- Returns `INVALID_HANDLE_VALUE` and sets `ERROR_OUTOFMEMORY` if the temporary event buffer cannot be allocated.
- The returned handle is owned by the caller, matching the public API contract in `dokan.h`.

Dependencies:
- Depends on `DOKAN_IO_EVENT`, `EVENT_INFORMATION`, and mount device naming from `dokani.h`.
- Uses `GetRawDeviceName()` and `SendToDevice()` from the core Dokan library.
- Uses driver FSCTL `FSCTL_GET_ACCESS_TOKEN`.

Notable risks:
- Assumes `FileInfo` and `FileInfo->DokanContext` are valid; only the decoded `ioEvent` fields are checked.
- The function shares one `EVENT_INFORMATION` buffer as both input and output, so the driver IOCTL contract must preserve this layout.
- A successful result may still return an invalid handle if the driver does so; no additional handle validation is performed.
