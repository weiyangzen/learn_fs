# File Research: sources/windows/winfsp/src/sys/close.c

Handles `IRP_MJ_CLOSE` for WinFsp devices.

Device variants:
- `FspFsctlClose()` dereferences a device stored in `FsContext2`.
- `FspFsvrtClose()` is a no-op success path.
- `FspFsvolClose()` handles volume file object close.

Volume close flow:
- Ignores invalid file objects.
- If cleanup did not complete, performs oplock check.
- Creates a must-succeed user-mode `Close` request populated with `UserContext` and `UserContext2`.
- Calls `FspFileNodeClose()`.
- Deletes the file descriptor and dereferences the file node.
- If a rename is active or IOQ pending count is above watermark, attaches request to the IRP and posts best-effort synchronously.
- Otherwise posts a best-effort work request and completes the close IRP immediately.

Completion:
- `FspFsvolCloseComplete()` only traces; actual state is already torn down.

Important behavior:
- Close cannot fail, and user-mode close notification is best-effort because the file-system may already be going away.
