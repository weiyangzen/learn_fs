# sources/sync-backup/restic/cmd/restic/cmd_debug_disabled.go

Purpose: non-debug build stub for debug command registration.

Control flow/state: build tag `!debug` compiles a `registerDebugCommand` function that accepts the root command/global options and intentionally registers nothing.

Dependencies/integration: paired with `cmd_debug.go` so the restic command tree can call `registerDebugCommand` unconditionally while normal builds omit debug commands.

Risks/test signals: very low risk; correctness is compile-time. Normal CI builds exercise this path.
