# sources/sync-backup/kopia/cli/command_blob_show.go

## Purpose
Low-level blob display command that reads a raw blob, optionally decrypts supported encrypted blob types, and formats JSON blobs through the shared output formatter.

## APIs, Types, and Functions
Important APIs include types `commandBlobShow`; functions/methods `setup`, `run`, `maybeDecryptBlob`, `canDecryptBlob`, `isJSONBlob`; Kingpin command(s) show: Show contents of BLOBs; flags decrypt: Decrypt blob if possible; arguments blobID: Blob IDs.

## Control Flow, State, and Persistence
Control flow registers command(s) show: Show contents of BLOBs, binds flags decrypt: Decrypt blob if possible, accepts arguments blobID: Blob IDs, then runs through a direct repository read action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches blob storage objects and metadata, content indexes, pack blobs, and content metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports bytes, context, encoding/json, io, github.com/pkg/errors, github.com/kopia/kopia/internal/blobcrypto, github.com/kopia/kopia/internal/gather, github.com/kopia/kopia/internal/iocopy, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/blob. It integrates with Kopia repository internals such as kopia/internal/blobcrypto, kopia/internal/gather, kopia/internal/iocopy, kopia/repo, kopia/repo/blob plus external packages bytes, context, encoding/json, io, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. nearby test file `sources/sync-backup/kopia/cli/command_blob_show_test.go` provides direct coverage.
