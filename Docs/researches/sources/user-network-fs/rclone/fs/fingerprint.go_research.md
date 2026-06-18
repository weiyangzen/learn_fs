<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fingerprint.go -->
# sources/user-network-fs/rclone/fs/fingerprint.go

## Purpose
Builds a compact change fingerprint for an object from size, optional modtime, and optional hash.

## Important APIs, Types, And Control Flow
`Fingerprint(ctx, o, fast)` always writes object size. It includes modtime when not in fast mode or when the backend does not mark modtime slow, and only if precision supports modtime. It includes one available hash when not in fast mode or hash is not marked slow, ignoring hash errors.

## State And Persistence
Pure computation over an `ObjectInfo`; no persistent state. It may call object methods that perform remote operations depending on backend feature flags.

## Dependencies And Integration Points
Used by operations that need a same-object change detector. Depends on `Fs.Features`, precision, hashes, object modtime/hash APIs.

## Risks And Test Signals
Not intended for cross-remote identity comparisons. Fast mode can omit important attributes for slow backends. Tests cover combinations of slow modtime/hash flags.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fingerprint.go -->
