# sources/sync-backup/kopia/repo/blob/sharded/sharded_parameters.go

Purpose: defines persisted sharding parameters and the algorithm mapping blob IDs to shard directories and remaining file names.

Important APIs/types/functions: `ParametersFile` is `.shards`; `PrefixAndShards` defines prefix-specific shard overrides; `Parameters` holds default shards, `UnshardedLength`, and overrides. `DefaultParameters`, `Load`, `Save`, `Clone`, `getShardsForBlobID`, and `GetShardDirectoryAndBlob` are the key functions.

Control flow: `GetShardDirectoryAndBlob` returns the root unchanged when the blob ID is short enough; otherwise it applies the first matching override or defaults, repeatedly moving leading ID segments into subdirectories until no segment can be taken.

State and persistence behavior: parameters are JSON-encoded in `.shards`. `Clone` deep-copies slice fields and overrides so later mutations cannot affect the clone.

Dependencies/integration: consumed by `sharded.Storage` and provider tests; uses path joins, JSON, and string prefix checks.

Risks and edge cases: override order controls matching. Shard sizes at or above remaining ID length stop further splitting. Misconfigured zero/negative values would produce unusual layouts, so tests emphasize representative valid specs.

Test signals: `TestShardedFileStorageShardingMap` validates default and override paths, short IDs, and prefix listing; `TestClone` verifies deep-copy isolation.
