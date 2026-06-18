# sources/sync-backup/kopia/internal/server/api_snapshots_test.go

Purpose: integration-tests snapshot list/delete/edit APIs.

Important APIs/types/functions: `TestListAndDeleteSnapshots` and `TestEditSnapshots`.

Control flow: creates snapshots in a test repository, lists through API, deletes selected snapshots, edits metadata/retention fields, and validates resulting API state.

State and persistence behavior: snapshot manifests in the temporary repository are created and mutated.

Dependencies and integration points: covers manifest conversion, retention fields, API client routing, and repository write sessions.

Risks and test signals: source action APIs such as pause/resume/upload need additional source-manager focused tests.
