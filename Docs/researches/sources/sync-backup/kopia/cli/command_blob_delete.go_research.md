# sources/sync-backup/kopia/cli/command_blob_delete.go

## Purpose
Low-level `blob delete` command that deletes a blob by ID directly from repository blob storage after repository write access is established.

## APIs, Types, and Functions
Important APIs include types `commandBlobDelete`; functions/methods `setup`, `run`; Kingpin command(s) delete: Delete blobs by ID; arguments blobIDs: Blob IDs.

## Control Flow, State, and Persistence
Control flow registers command(s) delete: Delete blobs by ID, accepts arguments blobIDs: Blob IDs, then runs through a direct repository write action. The implementation deletes blob storage objects. State and persistence: touches blob storage objects and metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, github.com/pkg/errors, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/blob. It integrates with Kopia repository internals such as kopia/repo, kopia/repo/blob plus external packages context, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: destructive modes require explicit confirmation/commit and should keep dry-run behavior tested. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
