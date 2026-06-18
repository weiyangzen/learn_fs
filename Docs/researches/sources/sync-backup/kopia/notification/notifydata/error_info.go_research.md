<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifydata/error_info.go -->
# sources/sync-backup/kopia/notification/notifydata/error_info.go

- Purpose: Defines structured notification payloads for operation errors.
- Important APIs/types/functions: `ErrorInfo`, `EventArgsType`, `StartTimestamp`, `EndTimestamp`, `Duration`, `NewErrorInfo`.
- Control flow: Accessors truncate start/end times to seconds and compute duration. Constructor captures operation metadata plus both simple and detailed error strings.
- State and persistence: JSON-serializable event payload; no repository persistence by itself.
- Dependencies and integration points: Used by maintenance/generic error notifications and template rendering.
- Risks and edge cases: Detailed error uses `%+v`; detail richness depends on wrapped error implementations.
- Test signals: `error_info_test.go` covers constructor, timestamps, duration, and round trip.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifydata/error_info.go -->
