# sources/sync-backup/restic/internal/fs/ea_windows.go

Purpose: Implements Windows extended attribute encoding/decoding and low-level NT API access.

Important APIs: `extendedAttribute`, `encodeExtendedAttributes`, `decodeExtendedAttributes`, `ntStatus.Err`, `fgetEA`, `fsetEA`, `getFileEA`, `setFileEA`, and `pathSupportsExtendedAttributes`.

Control flow and state: `fgetEA` repeatedly calls `NtQueryEaFile`, doubling the buffer on insufficient-buffer/more-data errors, returning nil for `STATUS_NO_EAS_ON_FILE`. `fsetEA` encodes all attributes and calls `NtSetEaFile`. NTSTATUS values are converted to DOS errors via `RtlNtStatusToDosErrorNoTeb`.

Dependencies and integration: Uses `go-winio` for EA binary layout, `x/sys/windows`, `ntdll.dll`, and unsafe syscalls. Called by Windows node metadata backup/restore in `node_windows.go`.

Risks: Unsafe syscall signatures are architecture-sensitive and tied to Windows NT internals. `fsetEA` indexes `encodedEA[0]`; callers must avoid passing empty encoded buffers. EA support varies by volume and is checked separately.

Test signals: `ea_windows_test.go` covers binary round-trips, no-final-padding decode, truncated decode errors, real file/folder set/get, and volume support detection.
