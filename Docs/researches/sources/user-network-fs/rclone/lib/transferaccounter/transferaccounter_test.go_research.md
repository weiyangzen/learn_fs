# sources/user-network-fs/rclone/lib/transferaccounter/transferaccounter_test.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/transferaccounter/transferaccounter_test.go -->
## sources/user-network-fs/rclone/lib/transferaccounter/transferaccounter_test.go

Purpose: tests context storage, byte accounting, reset behavior, and fallback no-op accounter.

Important APIs and control flow: `TestNew` creates an accounter with an add callback, checks initial not-started state, starts it, adds bytes, checks callback and internal total, then resets and expects totals to return to zero. `TestGet` covers retrieving an existing accounter, missing context values, and nil context. `TestNullAccounterBehavior` ensures no-op accounter calls do not panic and can be started.

State, dependencies, and integration: tests use a local integer accumulator and compare pointer identity for retrieved accounters. Dependencies are `context`, `testing`, and testify.

Risks and test signals: verifies main semantics. It does not test concurrent `Add` calls or reset races.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/transferaccounter/transferaccounter_test.go -->
