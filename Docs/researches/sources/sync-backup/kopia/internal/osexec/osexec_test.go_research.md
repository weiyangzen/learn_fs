# sources/sync-backup/kopia/internal/osexec/osexec_test.go

Purpose: verifies the portable `DisableInterruptSignal` API is callable for an `exec.Cmd`.

Important APIs/types/functions: `TestDisableInterruptSignal` constructs a command and calls `osexec.DisableInterruptSignal`.

Control flow: the test does not run the command; it asserts the helper can mutate command attributes without panicking.

State and persistence behavior: no persistent state or process execution.

Dependencies and integration points: tests the exported API from package `osexec_test`, so only public behavior is visible.

Risks and test signals: this is smoke coverage only. Platform-specific behavioral validation would need subprocess signal tests.
