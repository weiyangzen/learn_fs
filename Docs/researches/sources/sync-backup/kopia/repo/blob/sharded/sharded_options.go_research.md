# sources/sync-backup/kopia/repo/blob/sharded/sharded_options.go

Purpose: defines the shared option block embedded by providers that use directory sharding.

Important APIs/types/functions: `Options` contains `DirectoryShards []int` for shard segment sizes and optional `ListParallelism int` for parallel directory walking.

Control flow: `sharded.New` fills default `DirectoryShards` when nil: latest create mode uses `{1,3}` while open/legacy mode uses `{3,3}`. `ListBlobs` reads `ListParallelism`, defaulting to one worker.

State and persistence behavior: the effective directory-shard configuration can be persisted into `.shards` by `sharded.Storage`; the options themselves are also part of provider connection configs.

Dependencies/integration: anonymously embedded in SFTP, WebDAV, filesystem, and other sharded provider option structs.

Risks and edge cases: nil versus empty slices are meaningful. An explicit empty slice disables sharding in cache backing stores, while nil allows defaults.

Test signals: sharded and WebDAV tests run several shard specs and verify file paths/listing behavior.
