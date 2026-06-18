# File Research: sources/windows/winfsp/src/dll/wksid.c

Caches commonly used Windows well-known SIDs for DLL code.

Initialization:
- `FspWksidInitialize()` lazily allocates:
  - `WinWorldSid`,
  - `WinAuthenticatedUserSid`,
  - `WinLocalSystemSid`,
  - `WinServiceSid`.

APIs:
- `FspWksidNew(WellKnownSidType, PResult)` allocates `SECURITY_MAX_SID_SIZE`, calls `CreateWellKnownSid`, and returns the SID or sets an NTSTATUS error.
- `FspWksidGet(WellKnownSidType)` initializes once and returns the cached SID pointer for supported types.
- `FspWksidFinalize(Dynamic)` frees cached SIDs only during explicit dynamic unload.

Important behavior:
- Unsupported well-known SID types return `0`.
- Cached SIDs are process-wide static objects; callers should not free pointers returned by `FspWksidGet`.
