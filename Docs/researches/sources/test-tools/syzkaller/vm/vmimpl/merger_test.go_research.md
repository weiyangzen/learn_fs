# sources/test-tools/syzkaller/vm/vmimpl/merger_test.go

Purpose: unit tests for `OutputMerger` line buffering, tee output, error reporting, and decoder-state replacement.

Important APIs/types/functions: `TestMerger`, `brokenReader`, and `TestMergerErrors`.

Control flow: `TestMerger` creates two long pipes, writes partial data that must not emit until newline, verifies completed lines from each pipe, closes pipes to force EOF, checks `MergerError` fields, waits for merger shutdown, and compares tee content. `TestMergerErrors` adds a failing reader plus a hanging background pipe, verifies the first error, verifies the same error persists across `Errors` calls, re-adds the same decoder name with a new failure, and confirms the new error replaces the old state.

State and persistence: all state is in-memory pipes, a bytes buffer tee, and goroutines.

Dependencies and integration: uses `osutil.LongPipe`, `context`, `testify/assert`, and real `OutputMerger` APIs.

Risks: timing-dependent no-output checks use a short sleep; expected ordering matches current implementation rather than a fully robust interleaving model.

Test signals: direct coverage for line completeness, trailing newline insertion on close, tee serialization, EOF wrapping, and name replacement behavior.
