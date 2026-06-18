# File Research: sources/windows/winfsp/src/dll/eventlog.c

Windows Event Log integration for the WinFsp DLL.

Key responsibilities:
- Lazily registers an event source with `RegisterEventSourceW`.
- Provides `FspEventLog` and `FspEventLogV` formatted logging APIs.
- Maps information, warning, and error event types to WinFsp message IDs.
- Registers and unregisters the Event Log source under `HKLM\SYSTEM\CurrentControlSet\Services\EventLog\Application\<LIBRARY_NAME>`.
- Writes `EventMessageFile` and `TypesSupported` registry values.

Important behavior:
- Falls back from the library event source name to `FspDiagIdent()` if initial registration fails.
- `FspEventLogFinalize` deregisters only on explicit dynamic unload.
- Message strings include diagnostic identity and formatted message text.
- Registry registration resolves the DLL/module path with `MyEventLogRegisterPath`.

Dependencies:
- Includes `dll/library.h`, `stdarg.h`, and `eventlog/eventlog.h`.
- Uses Windows Event Log, registry, and module-path APIs.

Notable risks:
- Event source registration/unregistration requires appropriate registry privileges.
- Uses `wvsprintfW` into a 1024-wide-character buffer, matching the file’s own safety comment.
