# sources/sync-backup/kopia/internal/contentlog/contentlog_logger_test.go

Purpose: validates logger construction, nil-safe logging, typed log helpers from zero to six params, custom entries, multiple records, and error parameter handling.

Important APIs/types/functions: `TestNewLogger`, `TestLog`, `TestLog1` through `TestLog6`, `TestEmit`, `TestLoggerMultipleLogs`, `TestLoggerErrorHandling`, `customLogEntry`, and local `testError`.

Control flow: tests capture output into byte slices, emit logs with different helper functions, unmarshal JSON, and assert message field `m`, timestamp presence, logger params, context/custom params, and newline-delimited multi-entry behavior.

State and persistence behavior: in-memory capture only. Tests rely on output callbacks appending/copying bytes before writer release.

Dependencies/integration: uses `contentlog`, `logparam`, `encoding/json`, `strings`, and `testify/require`.

Risks/test signals: tests parse uint64/int64 through JSON float values, so they do not detect precision-preserving downstream requirements. They do not assert allocation counts; those are covered in `logparam` tests and benchmarks.
