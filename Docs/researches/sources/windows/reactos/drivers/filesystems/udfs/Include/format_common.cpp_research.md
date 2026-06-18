# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/format_common.cpp

Common formatter-side Win32 helpers for optical drive discovery, capability classification, and formatter drive locking.

Key responsibilities:
- Defines initial drive selection `szDisc` and changer flag `bChanger`.
- Implements `CheckCDType()` to open a CD/DVD volume, query cdrw.sys signature/device information/capabilities, and classify the media writer type.
- Implements `InitDeviceList()` to enumerate logical drives, filter CD-ROM drives, classify each one, and pass display data to a caller-provided callback.
- Implements `FmtAcquireDrive()`, `FmtIsDriveAcquired()`, and `FmtReleaseDrive()` using named public events as per-drive/per-level formatter locks.

Important behavior:
- `CheckCDType()` returns `BUSY` if the target cannot be opened, `OTHER` for unsupported or unknown media, and more specific writer types for CD-R, CD-RW, DVD-R, DVD-RW, DVD+RW, or DVD-RAM.
- Device capabilities come from both capability bitmasks and GET CONFIGURATION feature flags, with DVD-RAM and rewritable formats prioritized before CD formats.
- `InitDeviceList()` builds a comma-separated copy of `GetLogicalDriveStrings()` output by replacing NUL separators, then parses it with `strtok()`.
- Formatter acquisition creates `DwFmtLock_<Drive><Level>` events; an existing event means the drive is already acquired at that level.

Dependencies:
- Uses Win32 drive APIs, `OpenOurVolume()`, `UDFPhSendIOCTL()`, cdrw.sys private IOCTLs, `GET_SIGNATURE_USER_OUT`, `GET_DEVICE_INFO_USER_OUT`, `GET_CAPABILITIES_USER_OUT`, capability constants, and `MediaTypeStrings`.
- Public prototypes are declared in `format_common.h`.

Notable risks:
- The code is ANSI-oriented and casts buffers through `LPTSTR`, so Unicode/MBCS build settings matter.
- `InitDeviceList()` mutates the logical-drive buffer with `memchr(Buffer, '\0', MAX_PATH)` repeatedly from the start; it relies on the comma replacement eventually reaching a comma before a zero.
- Drive lock names only use the first drive character and a single level byte, so the lock namespace is intentionally coarse.
