# Research: sources/user-network-fs/rclone/fs/rc/internal_test.go

## sources/user-network-fs/rclone/fs/rc/internal_test.go

Purpose: tests internal/core rc endpoints. `TestMain` simulates current-binary behavior for `core/command` by intercepting `version` and `unknown_command` arguments.

Control flow tests noop echo, error, command list, pid type, memory stats, GC nil output, version fields, obscure/reveal, quit parameter validation, `core/command` combined and streaming return types, and `core/disks` output shape. State touched includes process args in `TestMain`, runtime memory reads, HTTP recorder bodies, and current executable subprocesses. Dependencies include `httptest`, `obscure`, `fs.Version`, runtime info, and rc call registry. Integration signal is high for GUI/API clients using core endpoints. Risks covered include subprocess error handling, stdout/stderr stream routing, required response writer, non-empty disk paths, and platform-dependent version fields. Destructive paths like successful `core/quit` are intentionally not executed.
