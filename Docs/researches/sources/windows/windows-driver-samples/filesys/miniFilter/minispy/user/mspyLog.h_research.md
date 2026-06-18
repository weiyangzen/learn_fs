# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/minispy/user/mspyLog.h

User-mode MiniSpy logging header.

Key contents:
- Includes `fltUser.h` and shared `minispy.h`.
- Defines `BUFFER_SIZE` = 4096 for batched log retrieval.
- Defines `LOG_CONTEXT`, holding the MiniSpy port, screen/file logging toggles, output file handle, cleanup flag, and shutdown semaphore.
- Declares `RetrieveLogRecords`, `FileDump`, and `ScreenDump`.
- Re-declares user-mode values for `FLT_CALLBACK_DATA_*` operation-type flags.
- Provides string constants for standard IRP major codes, FltMgr pseudo-major codes, Fast I/O-like major codes, IRP minor codes, PnP/power/system-control minors, and transaction notification names.
- Defines local numeric IRP major/minor values needed by the formatter.
- Defines `TRANSACTION_NOTIFICATION_CODES`, aligned with kernel-side `TxNotificationToMinorCode`.
- Defines `FLT_TAG_DATA_BUFFER` so the user utility can interpret file-tag/reparse log records.

Important behavior:
- This header intentionally mirrors kernel/FltMgr constants so the user program can decode logs without including kernel headers.
- Transaction notification code ordering is tied to the bit-position conversion in `mspyLib.c`.

Dependencies and risks:
- Duplicate definitions must stay synchronized with kernel logging behavior and with Windows/FltMgr values.
- The local `FLT_TAG_DATA_BUFFER` is only a display helper for reparse data placed in the log name area.
