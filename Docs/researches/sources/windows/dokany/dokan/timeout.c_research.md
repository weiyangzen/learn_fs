# File Research: sources/windows/dokany/dokan/timeout.c

Implements `DokanResetTimeout`, allowing user callbacks to extend/reset a pending operation timeout.

Key behavior:
- Retrieves the active `DOKAN_IO_EVENT` from `FileInfo->DokanContext`.
- Validates event context and instance.
- Allocates an `EVENT_INFORMATION`, fills serial number and requested timeout.
- Sends `FSCTL_RESET_TIMEOUT` to the raw device name.
- Frees the event info and returns the `SendToDevice` result.
- Sets `ERROR_INVALID_PARAMETER` or `ERROR_OUTOFMEMORY` on local validation/allocation failures.

Role:
- Lets long-running filesystem callbacks keep the driver-side request from timing out.
