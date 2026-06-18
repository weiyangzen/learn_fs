# sources/sync-backup/kopia/internal/contentlog/logparam/logparam.go

Purpose: supplies typed parameter constructors that write fields into `contentlog.JSONWriter`.

Important APIs/types/functions: `String`, `Int64`, `Int`, `Int32`, `Bool`, `Time`, `Error`, `UInt64`, `UInt32`, `Duration`, and param structs implementing `WriteValueTo`.

Control flow: each constructor returns a small value struct containing key and typed value. `WriteValueTo` dispatches to the matching JSON writer field method. `Duration` logs microseconds, and `Error` logs `null` for nil.

State and persistence behavior: no mutable state. Values are intended to be stack-friendly and zero-allocation when used directly.

Dependencies/integration: imports `contentlog` and `time`. Used by content logging callers, especially epoch manager diagnostics.

Risks/test signals: caller-provided keys are not escaped beyond JSON string field writing, and duplicate keys are allowed. Duration truncates sub-microsecond values. Tests assert output and zero allocations for constructors and writer methods.
