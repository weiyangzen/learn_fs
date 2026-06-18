# sources/sync-backup/kopia/repo/content/stats.go

## Purpose
Defines thread-safe counters for content manager activity: content reads/writes/hashes, byte totals, encryption/decryption bytes, and valid/invalid content findings.

## Important APIs, Types, And Functions
`Stats` contains `atomic.Int64` and `atomic.Uint32` fields. Public methods are `Reset`, `ReadContent`, `WrittenContent`, `HashedContent`, `DecryptedBytes`, `EncryptedBytes`, `InvalidContents`, and `ValidContents`. Package-private increment helpers include `decrypted`, `encrypted`, `readContent`, `wroteContent`, `hashedContent`, `foundValidContent`, and `foundInvalidContent`.

## Control Flow
Readers load atomic values and return approximate snapshots. Writers increment byte and count fields independently, so count/byte pairs are eventually consistent rather than a single atomic tuple. `Reset` stores zero to all counters.

## State And Persistence
State is in-memory only and belongs to a `Stats` instance. There is no persistence or external synchronization beyond atomic operations.

## Dependencies And Integration Points
The only dependency is `sync/atomic`. Content read/write, hashing, encryption, and verification code can update these counters without taking locks.

## Risks And Edge Cases
`Reset` is not an atomic global transaction; concurrent readers or writers can observe mixed old/new values. Public comments describe counts as approximate, which is important for UI/progress use. There is a comment typo on `EncryptedBytes`, which says decrypted bytes.

## Test Signals
No dedicated tests in this subset. The design is simple enough that indirect coverage comes from content manager tests that update stats during operations.
