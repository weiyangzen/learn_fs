<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/restic/restic_appendonly_test.go -->
# sources/user-network-fs/rclone/cmd/serve/restic/restic_appendonly_test.go

Source read: complete file, 137 lines, 3509 bytes, sha256 `a6b42891dc768371e30461f76f46e09b4a295f4026390141f554f26c534ef0b9`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/restic/restic_appendonly_test.go_research.md`.

## Purpose
Tests restic server append-only mode, especially overwrite and delete restrictions.

## Important APIs, types, and functions
`createOverwriteDeleteSeq` builds reusable request sequences. `TestResticHandler` creates a local-backed server with `AppendOnly=true`, creates a repo, and runs sequences for config, data objects, and lock files.

## Control flow
Each sequence uses httptest requests directly against the chi router and checks HTTP status/body after POST, GET, and DELETE operations.

## State and persistence behavior
State is a temporary local repository. Append-only should preserve original object contents after forbidden overwrite/delete while allowing lock creation and lock deletion.

## Dependencies and integration points
Depends on `cmd.NewFsSrc`, configfile install, restic request helpers, and HTTP status assertions.

## Risks and edge cases
Random IDs avoid collisions but the test only covers REST handler semantics, not concurrent restic clients.

## Test signals
Strong signal that append-only protects repository data but permits lock cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/restic/restic_appendonly_test.go -->
