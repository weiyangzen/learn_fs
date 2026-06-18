# sources/sync-backup/kopia/cli/command_manifest_show.go

## Purpose
Raw manifest show command that fetches manifest payloads by ID and renders them as JSON through the output formatter.

## APIs, Types, and Functions
Important APIs include types `commandManifestShow`; functions/methods `setup`, `toManifestIDs`, `showManifestItems`; Kingpin command(s) show: Show manifest items; arguments item: List of items.

## Control Flow, State, and Persistence
Control flow registers command(s) show: Show manifest items, accepts arguments item: List of items, then runs through a repository reader action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches repository manifest metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports bytes, context, encoding/json, github.com/pkg/errors, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/manifest. It integrates with Kopia repository internals such as kopia/repo, kopia/repo/manifest plus external packages bytes, context, encoding/json, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
