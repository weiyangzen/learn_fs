# sources/sync-backup/kopia/cli/command_content_show.go

## Purpose
Content display command that opens a content ID from the repository and streams bytes to stdout through the shared output path.

## APIs, Types, and Functions
Important APIs include types `commandContentShow`; functions/methods `setup`, `run`, `contentShow`; Kingpin command(s) show: Show contents by ID.; flags json: Pretty-print JSON content, unzip: Transparently decompress the content; arguments id: IDs of contents to show.

## Control Flow, State, and Persistence
Control flow registers command(s) show: Show contents by ID., binds flags json: Pretty-print JSON content, unzip: Transparently decompress the content, accepts arguments id: IDs of contents to show, then runs through a direct repository read action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches content indexes, pack blobs, and content metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports bytes, context, github.com/pkg/errors, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/content. It integrates with Kopia repository internals such as kopia/repo, kopia/repo/content plus external packages bytes, context, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
