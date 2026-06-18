<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/retryable.go -->
## sources/storage-engines/pebble/metamorphic/retryable.go

Purpose: provides retry semantics for metamorphic tests running under injected filesystem errors, especially iterator operations that may fail transiently and need to be retried without changing expected test history.

Important APIs and types: `RetryPolicy` decides whether an error is retryable. `NeverRetry` and `RetryInjected` are built-in policies, with `RetryInjected` matching `errorfs.ErrInjected`. `withRetries` repeatedly invokes a function until the returned error is not retryable. `retryableIter` wraps `*pebble.Iterator` and implements the subset of iterator methods used by metamorphic ops.

Control flow: `retryableIter.withRetry` runs an iterator action, inspects `iter.Error`, and if retryable keeps repositioning with `SeekGE(lastKey)` until the iterator clears the retryable error. It then records the current key as the new `lastKey` if valid. Positioning methods (`First`, `Last`, `Next`, `Prev`, `SeekGE`, `SeekLT`, limit variants, `NextPrefix`, `SeekPrefixGE`) all delegate through `withRetry`; accessors and option setters pass through directly.

State and persistence: `lastKey` is the only local state. It represents the successful post-operation iterator position used to reconstruct pre-operation state during retries. No persistent state is written.

Dependencies and integration: used by `Test.setIter` in `test.go`; retry policies are supplied by `TestOptions`. Depends on Pebble iterator APIs and `vfs/errorfs` injected errors.

Risks and edge cases: retry recovery assumes `SeekGE(lastKey)` is a valid way to return to the previous state, which may not model all reverse-iteration states perfectly. A retry policy that returns true forever could loop indefinitely. `SetBounds` and `SetOptions` are not retried here.

Test signals: coverage is indirect through metamorphic tests using injected errors; this file has no dedicated unit test in the listed set.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/retryable.go -->
