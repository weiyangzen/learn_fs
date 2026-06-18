# sources/storage-engines/foundationdb/fdbcli/RangeLockCommand.cpp

Purpose: Implements `rangelock`, a user-facing range lock management command for registering owners, taking/releasing exclusive read locks, releasing all locks for an owner, and listing locks.

Important APIs/types/functions: `rangeLockCommandActor(Database, tokens)`, `printKnobReminder`, `parseNormalKeyRange`, `reportRangeLockError`, `registerRangeLockOwner`, `removeRangeLockOwner`, `getAllRangeLockOwners`, `takeExclusiveReadLockOnRange`, `releaseExclusiveReadLockOnRange`, `releaseExclusiveReadLockByUser`, `findExclusiveReadLockOnRange`, `RangeLockOwner`, and `RangeLockState`.

Control flow: The actor dispatches on subcommands. `register` and `unregister` validate non-empty owner IDs/descriptions and call owner management APIs. `owners` lists all owners. `take` and `release` validate owner ID and a strict non-empty range within `normalKeys`, then call the range lock API. `release-all` releases every lock by owner. `list` scans either `normalKeys` or a supplied normal range and prints locks. Range-lock API errors are mapped to tailored messages; actor cancellation is rethrown.

State and persistence behavior: Persists owner and lock metadata through fdbclient range-lock management APIs. Lock enforcement depends on commit proxies being started with `knob_enable_read_lock_on_range=true`; the command prints a reminder after taking a lock because metadata alone may not reject writes.

Dependencies and integration points: Depends on `fdbclient/RangeLock.h`, `ManagementAPI`, normal keyspace constants, and fdbcli command registration. Bulk-load debug paths also use related range-lock helpers.

Risks: Enforcement knob cannot be probed by the client, so users can get persisted but unenforced locks. Release requires matching range/owner semantics, which may be surprising. All operations have high coordination impact if lock metadata is wrong.

Test signals: Cover every subcommand, invalid arity, empty owner/description, invalid and system key ranges, overlapping lock errors, unlock reject errors, owner lifecycle, list filtering, knob reminder text, and actor-cancelled propagation.
