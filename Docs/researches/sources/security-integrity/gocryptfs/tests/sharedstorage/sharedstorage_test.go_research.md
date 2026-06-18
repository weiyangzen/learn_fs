# sources/security-integrity/gocryptfs/tests/sharedstorage/sharedstorage_test.go

## Purpose
Tests behavior when the same gocryptfs cipherdir is mounted twice, with and without the `-sharedstorage` cache-coherency option.

## Important APIs, Types, And Functions
- `TestMain` runs the whole package once without and once with `-sharedstorage`.
- `testCase` stores cipherdir and two mountpoints.
- `newTestCase`, `cleanup`, and `mountSharedstorage` manage paired mounts.
- `TestDirUnlink` replaces a directory with a file through one mount and unlinks through the other.
- `TestStaleHardlinks` creates and deletes hardlinks across mounts, then opens the surviving link.

## Control Flow
Each test creates a fresh initialized cipherdir and mounts it twice. Mutations through one mount intentionally stale the other mount's cache; the test either expects immediate success under `-sharedstorage` or success after the entry timeout expires.

## State And Persistence
State is a temporary cipherdir with two live FUSE mounts. `waitForExpire` reflects the one-second kernel entry timeout plus margin.

## Dependencies And Integration Points
Depends on `golang.org/x/sys/unix` and `test_helpers` mount lifecycle helpers.

## Risks And Edge Cases
Without `-sharedstorage`, the tests encode timeout-based eventual correctness, which can be timing-sensitive. With `-sharedstorage`, stale-cache failures are fatal immediately.

## Test Signals
Signals are successful cross-mount unlink/open behavior in sharedstorage mode and after cache expiration in normal mode.
