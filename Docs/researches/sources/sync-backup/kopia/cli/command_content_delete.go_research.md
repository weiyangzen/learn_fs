# sources/sync-backup/kopia/cli/command_content_delete.go

## Purpose
Content deletion command that marks repository content IDs as deleted, with support for range selection through shared content range flags.

## APIs, Types, and Functions
Important APIs include types `commandContentDelete`; functions/methods `setup`, `run`; Kingpin command(s) delete: Remove content; arguments id: IDs of content to remove.

## Control Flow, State, and Persistence
Control flow registers command(s) delete: Remove content, accepts arguments id: IDs of content to remove, then runs through a direct repository write action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches content indexes, pack blobs, and content metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, github.com/pkg/errors, github.com/kopia/kopia/repo. It integrates with Kopia repository internals such as kopia/repo plus external packages context, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: destructive modes require explicit confirmation/commit and should keep dry-run behavior tested. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
