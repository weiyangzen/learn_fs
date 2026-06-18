# File Research: sources/windows/winfsp/src/sys/debug.c

Debug-only symbolization and IRP logging helpers, compiled under `#if DBG`.

Symbol helpers:
- `NtStatusSym()` maps NTSTATUS values, plus WinFsp IOQ pseudo-statuses, to strings; includes generated `ntstatus.i`.
- `IrpMajorFunctionSym()` maps major IRP codes.
- `IrpMinorFunctionSym()` maps minor IRP codes for read/write, directory control, file-system control, lock control, power, system control, and PNP.
- `IoctlCodeSym()` maps WinFsp IOCTLs and generated IOCTL constants from `ioctl.i`.
- `FileInformationClassSym()` maps many `FILE_INFORMATION_CLASS` values, including explicit numeric cases for `FileStatInformation` and `FileStatLxInformation`.
- `FsInformationClassSym()` maps file-system info classes.
- `DeviceExtensionKindSym()` maps WinFsp extension kinds to short labels.

Other utilities:
- `DebugRandom()` implements a spinlock-protected ucrt-style deterministic PRNG.
- `FspDebugLogIrp()` prints current IRQL, function, IRP pointer, device kind, requestor mode, major/minor operation, NTSTATUS symbol, and IoStatus information.

Important behavior:
- No runtime effect in non-debug builds.
- Includes generated symbol tables to keep logs readable during kernel debugging.
