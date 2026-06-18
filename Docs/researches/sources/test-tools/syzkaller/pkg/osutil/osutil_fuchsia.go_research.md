# sources/test-tools/syzkaller/pkg/osutil/osutil_fuchsia.go

Purpose: Fuchsia-specific interrupt and process-exit helpers.

Important APIs: `HandleInterrupts` is a no-op on Fuchsia. `ProcessExitStatus` currently returns 0 with a TODO to parse status text.

Control flow and state: No state; both functions are simple platform shims selected by `//go:build fuchsia`.

Dependencies and integration: Provides the platform-specific functions expected by code using osutil process helpers.

Risks: Returning 0 for all Fuchsia process statuses can hide failures in callers relying on exit codes. No-op interrupt handling means graceful shutdown semantics differ from Unix.

Test signals: No direct tests in this shard.
