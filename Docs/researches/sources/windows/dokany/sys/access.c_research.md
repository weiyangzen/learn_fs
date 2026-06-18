# File Research: sources/windows/dokany/sys/access.c

## Role

Implements `DokanGetAccessToken`, a kernel IOCTL helper that returns an access token handle for a pending create IRP.

## Main Function

- `DokanGetAccessToken(PREQUEST_CONTEXT RequestContext)`

## Behavior

- Requires the IOCTL to come from user mode.
- Validates the output buffer is exactly `sizeof(EVENT_INFORMATION)`.
- Looks up a pending IRP by `SerialNumber` in `Dcb->PendingIrp`.
- Expects the target pending IRP to be an `IRP_MJ_CREATE` with a security context.
- Extracts the subject token from the create IRP access state.
- Opens a kernel handle to the token using `ObOpenObjectByPointer`.
- Returns that handle in `eventInfo->Operation.AccessToken.Handle`.

## Dependencies

- `dokan.h`
- `util/irp_buffer_helper.h`
- Pending IRP list locking via spin lock.
- Windows security APIs:
  - `SeQuerySubjectContextToken`
  - `ObOpenObjectByPointer`
  - `SeTokenObjectType`

## Notes and Risks

- Protects pending IRP list traversal with `PendingIrp.ListLock`.
- Explicitly avoids accessing `SeTokenObjectType` while holding the spin lock because that caused BSODs on Windows XP.
- Failure to find the matching pending IRP leaves status as `STATUS_INVALID_PARAMETER`.
