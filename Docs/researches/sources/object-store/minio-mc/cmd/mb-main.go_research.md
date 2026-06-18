# Research: sources/object-store/minio-mc/cmd/mb-main.go

## sources/object-store/minio-mc/cmd/mb-main.go

Purpose: implements `mc mb`, creating object-storage buckets or filesystem directories, with optional region, ignore-existing, object-lock, and versioning behavior.

Important APIs and functions: `mbCmd` defines the CLI command and examples; `makeBucketMessage` implements the shared `message` contract with `String` and `JSON`; `checkMakeBucketSyntax` enforces at least one target; `mainMakeBucket` performs the operation.

Control flow: after syntax validation and color setup, `mainMakeBucket` iterates all targets. It creates a `Client` via `newClient`, creates a per-target cancellable context, calls `MakeBucket(region, ignoreExisting, withLock)`, optionally calls `SetVersion("enable")`, and prints success. Per-target failures set a final error status but allow later targets to continue.

State and persistence: bucket/directory creation and optional bucket versioning are persistent remote or filesystem mutations. No local state is written except normal global config reads done before command dispatch.

Dependencies and integration: uses `Client.MakeBucket`, `Client.SetVersion`, `BucketNameEmpty`, `urlJoinPath`, shared output printing, and global CLI flags.

Risks and tests: the defer in the loop delays cancellation until command exit for every target. Versioning failure is fatal after bucket creation, so partial success is possible. There are no direct tests in this subset for `mb`; coverage is integration-dependent.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/mb-main.go -->
