## sources/object-store/minio-mc/pkg/probe/probe.go

Purpose: tracing error wrapper used across mc to preserve cause, call trace, system info, and app metadata. Important APIs are `Init`, `SetAppInfo`, `GetSysInfo`, `NewError`, `(*Error).Trace`, `Untrace`, `ToGoError`, and `String`.

Control flow captures root path from the caller of `Init`, initializes app metadata, captures host/runtime/memory details for each new error, and appends trace points from callers. `String` prints the cause, reverse call trace, app info, and system details. State includes global `rootPath` and `appInfo`, plus per-error locked trace slices. Dependencies are runtime, filesystem paths, hostname, humanized memory, and sync locks. Risks include global map writes without locking, missing `Init` causing untrimmed paths, and verbose error strings leaking host/app data. Tests cover trace creation and wrapping.
