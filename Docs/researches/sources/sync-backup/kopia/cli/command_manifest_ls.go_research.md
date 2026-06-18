# sources/sync-backup/kopia/cli/command_manifest_ls.go

## Purpose
Raw manifest listing command that filters manifests by labels and sorts output by selected label keys.

## APIs, Types, and Functions
Important APIs include types `commandManifestList`; functions/methods `setup`, `listManifestItems`, `sortedMapValues`; Kingpin command(s) list: List manifest items; flags filter: List of key:value pairs, sort: List of keys to sort by.

## Control Flow, State, and Persistence
Control flow registers command(s) list: List manifest items, binds flags filter: List of key:value pairs, sort: List of keys to sort by, then runs through a repository reader action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches repository manifest metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, fmt, sort, strings, github.com/pkg/errors, github.com/kopia/kopia/repo. It integrates with Kopia repository internals such as kopia/repo plus external packages context, fmt, sort, strings, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
