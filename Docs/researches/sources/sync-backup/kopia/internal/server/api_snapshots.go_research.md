# sources/sync-backup/kopia/internal/server/api_snapshots.go

Purpose: implements snapshot listing, deletion, editing, upload trigger, cancellation, pause/resume, filtering, and manifest conversion APIs.

Important APIs/types/functions: `handleListSnapshots`, `handleDeleteSnapshots`, `handleEditSnapshots`, `forAllSourceManagersMatchingURLFilter`, `handleUpload`, `handleCancel`, `handlePause`, `handleResume`, `uniqueSnapshots`, `sourceMatchesURLFilter`, and `convertSnapshotManifest`.

Control flow: list loads snapshot manifests, converts them to API rows, and de-duplicates. Delete/edit operate on selected snapshot manifests in write sessions. Source actions iterate source managers matching URL filters and invoke snapshot, cancel, pause, or resume operations. Conversion maps manifest metadata, retention, statistics, and source fields into `serverapi.Snapshot`.

State and persistence behavior: delete/edit mutate snapshot manifests and retention labels; upload starts background source-manager tasks; pause/resume/cancel mutate source manager runtime state.

Dependencies and integration points: integrates `snapshot`, `manifest`, `policy`, `sourceManager`, server task management, and UI source controls.

Risks and test signals: filtering by host/user/path and manifest de-duplication are subtle; write actions require proper authorization and refresh. Tests cover list/delete/edit flows.
