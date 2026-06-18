# sources/sync-backup/kopia/cli/command_blob_list.go

## Purpose
Low-level blob listing command with prefix, exclusion, size, and data-only filters. It walks storage metadata and formats blob IDs, lengths, timestamps, and storage IDs.

## APIs, Types, and Functions
Important APIs include types `commandBlobList`; functions/methods `setup`, `run`, `shouldInclude`; Kingpin command(s) list: List BLOBs; flags prefix: Blob ID prefix, exclude-prefix: Blob ID prefixes to exclude, min-size: Minimum size, max-size: Maximum size, data-only: Only list data blobs.

## Control Flow, State, and Persistence
Control flow registers command(s) list: List BLOBs, binds flags prefix: Blob ID prefix, exclude-prefix: Blob ID prefixes to exclude, min-size: Minimum size, max-size: Maximum size, data-only: Only list data blobs, then runs through a direct repository read action. The implementation iterates blob storage. State and persistence: touches blob storage objects and metadata, encrypted repository log blobs, content index blobs and epoch metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, strings, github.com/kopia/kopia/internal/epoch, github.com/kopia/kopia/internal/repodiag, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/blob, github.com/kopia/kopia/repo/content/indexblob. It integrates with Kopia repository internals such as kopia/internal/epoch, kopia/internal/repodiag, kopia/repo, kopia/repo/blob, kopia/repo/content/indexblob plus external packages context, strings.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
