# File Research: sources/windows/dokany/sys/util/log.c

Dokan kernel logging implementation for debug prints, Windows Event Log entries, stringification helpers, and cached driver-log delivery to user mode.

Key responsibilities:
- Defines global debug/cache state: `g_Debug`, `g_DokanDriverLogCacheEnabled`, `g_DokanVcbDriverLogCacheCount`, and `g_DokanLogEntryList`.
- Writes formatted wide-character messages to the Windows Event Log via `IO_ERROR_LOG_PACKET`.
- Provides `DokanLogError` and `DokanLogInfo`.
- Captures compact stack traces for diagnostic logging.
- Converts NTSTATUS, IRP major/minor codes, file information classes, filesystem information classes, identifier types, create results, and IOCTLs to readable strings.
- Caches formatted driver log messages and dispatches them to userland as `DOKAN_IRP_LOG_MESSAGE` events.
- Cleans cached log entries associated with a volume during teardown.

Important behavior:
- Event Log messages are capped at `DOKAN_LOG_MAX_CHAR_COUNT` and split into multiple `IO_ERROR_LOG_PACKET`s when they exceed one packet’s string capacity.
- Event Log writing is skipped above `PASSIVE_LEVEL`.
- Cached log entries are capped at 1024; when full, the oldest entry is dropped.
- `PushDokanLogEntry` skips per-volume logs when the volume did not request driver log dispatch.
- `PopDokanLogEntry` sends both global logs and logs for the target VCB, then removes sent entries from the global cache.
- `IsLogCacheEnabled` avoids expensive log formatting unless global or per-volume caching is active.
- `CleanDokanLogEntry` decrements the active cached-log VCB count and removes all cached entries tied to that volume.

Dependencies:
- Includes `log.h`, Dokan core headers, mount/storage Windows headers, and generated include files `ntstatus_log.inc` and `ioctl.inc`.
- Uses Dokan allocation, resource locking, event context allocation, and `DokanEventNotification`.
- Uses Windows kernel routines such as `IoAllocateErrorLogEntry`, `IoWriteErrorLogEntry`, `RtlStringCchVPrintfW`, `RtlStringCchVPrintfExA`, `RtlCaptureStackBackTrace`, and time/query helpers through macros.

Notable risks:
- Cached logging requires `PASSIVE_LEVEL`; high-IRQL callers only debug-print.
- `PopDokanLogEntry` returns without removing entries if event allocation fails, leaving later retry possible but delaying dispatch.
- The global cache mixes global entries and VCB-specific entries, so correct VCB cleanup is important during teardown.
- Stringification tables are manually curated plus generated includes; unknown values fall back to `"Unknown"` or related sentinel strings.
