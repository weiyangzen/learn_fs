# sources/sync-backup/restic/cmd/restic/cmd_list_integration_test.go

Purpose: helper and integration coverage for `restic list`, especially blob enumeration.

Important APIs/types/functions: `testRunList`; `parseIDsFromReader`; `testListSnapshots`; `testListBlobs`; `TestListBlobs`.

Control flow and state: helpers capture stdout, parse either bare 64-character IDs or `type id` blob lines, and return `restic.IDs`. The blob test creates a backup, runs `list blobs`, builds an ID set, independently opens the repo, loads the index, calls `repo.ListBlobs`, and compares sets.

Dependencies and integration points: depends on backup test helpers, repository index loading, ID parsing, and stdout capture.

Risks: parser assumes any non-64-char line ends with an ID, so unrelated output could be misparsed. The test compares blob IDs but not blob type counts.

Test signals: validates that `runList("blobs")` sees the same blob IDs as the repository index API.
