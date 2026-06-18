# sources/user-network-fs/gcsfuse/internal/fs/inode/lookup_count.go

## Purpose

`lookup_count.go` provides a small helper embedded by inode implementations to track kernel lookup references. FUSE lookup counts decide when the filesystem must continue remembering an inode and when it can destroy local resources after forget operations reduce the count to zero.

## Important APIs, Types, And Functions

`lookupCount` stores the inode ID, current unsigned count, and a `destroyed` flag. `Init` records the inode ID for diagnostics. `Inc` increments the count and panics if the helper has already been destroyed. `Dec` decrements by a caller-provided amount, panics if destroyed or if `n` exceeds the current count, and returns true when the count reaches zero.

The helper is intentionally unexported and requires external synchronization. Concrete inodes call it while holding their own invariant mutexes, as seen in `FileInode.IncrementLookupCount`/`DecrementLookupCount` and directory equivalents.

## Control Flow And State Behavior

The state machine is simple: initialized count starts at zero, increments follow lookup responses, decrements follow forgets, and a zero result tells the caller to destroy the inode. The `destroyed` field is checked but not set in this file, so callers or embedding code would need to set it if they want post-destroy panic protection. In the current requested code, the main visible behavior is over-decrement protection and zero-count signaling.

No persistence exists. The count is process-local inode-manager state and is lost when the filesystem process exits.

## Dependencies And Integration Points

The file depends on `fmt` and FUSE inode IDs. It integrates with the `Inode` interface's lookup-count methods and with any inode manager that calls `Destroy` after `Dec` returns true. Panic messages include the inode ID where available, making internal misuse easier to diagnose during invariant-enabled tests.

## Risks And Test Signals

The important risk is misuse under missing locks or mismatched forget counts, either of which can corrupt lifecycle management. Another subtle point is that `destroyed` is not changed by `Dec`; if expected, that behavior must be implemented by embedding code. `dir_test.go` includes a lookup count test that increments three times and verifies destruction is signaled only after all three references are decremented. There is no direct panic-path test in the requested subset.
