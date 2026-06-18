# sources/sync-backup/kopia/cli/command_blob_shards_modify.go

## Purpose
Offline sharded-storage layout migration command. It parses shard parameters, computes new blob paths, optionally dry-runs, renames blob files, and removes empty directories after confirmation no Kopia process is running.

## APIs, Types, and Functions
Important APIs include types `commandBlobShardsModify`; functions/methods `setup`, `getParameters`, `parseShardSpec`, `prefixAndShardsWithout`, `applyParameterChangesFromFlags`, `run`, `removeEmptyDirs`, `renameBlobs`; Kingpin command(s) modify: Perform low-level resharding of blob storage; flags i-am-sure-kopia-is-not-running: Confirm that no other instance of kopia is running, path: Sharded directory path, default-shards: Default specification 'n1,..nN' or 'flat'), override: Override specification 'prefix=n1,..nN'), remove-override: Override specification 'prefix=n1,..nN'), unsharded-length: Minimum sharded length, dry-run: Dry run.

## Control Flow, State, and Persistence
Control flow registers command(s) modify: Perform low-level resharding of blob storage, binds flags i-am-sure-kopia-is-not-running: Confirm that no other instance of kopia is running, path: Sharded directory path, default-shards: Default specification 'n1,..nN' or 'flat'), override: Override specification 'prefix=n1,..nN'), remove-override: Override specification 'prefix=n1,..nN'), unsharded-length: Minimum sharded length, dry-run: Dry run, then runs through a no-repository action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches blob storage objects and metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, fmt, os, path, path/filepath, strconv, strings, github.com/pkg/errors, github.com/kopia/kopia/repo/blob, github.com/kopia/kopia/repo/blob/sharded. It integrates with Kopia repository internals such as kopia/repo/blob, kopia/repo/blob/sharded plus external packages context, fmt, os, path, path/filepath, plus 3 more.

## Risks and Test Signals
Risks and test signals: filesystem operations are platform and permission sensitive. nearby test file `sources/sync-backup/kopia/cli/command_blob_shards_modify_test.go` provides direct coverage.
