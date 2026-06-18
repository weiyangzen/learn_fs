<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/serverapi/serverapi.go -->
# sources/sync-backup/kopia/internal/serverapi/serverapi.go

- Purpose: Defines the JSON request/response contract for Kopia server APIs.
- Important APIs/types/functions: `StatusResponse`, `SourcesResponse`, `SourceStatus`, `PolicyListEntry`, `PoliciesResponse`, `Empty`, `APIErrorCode`, `ErrorResponse`, `SourceActionResponse`, `MultipleSourceActionResponse`, `CreateRepositoryRequest`, `ConnectRepositoryRequest`, `SupportedAlgorithmsResponse`, `Snapshot`, `RestoreRequest`, `EstimateRequest`, `ResolvePolicyRequest`, `ResolvePolicyResponse`, `UIPreferences`.
- Control flow: This file is declarative; server handlers and clients marshal/unmarshal these structs.
- State and persistence: Struct fields expose repository configuration, source status, snapshots, tasks, policies, restore/estimate inputs, and UI preferences; persistence is owned by the server and repository layers.
- Dependencies and integration points: Integrates `fs`, `uitask`, `repo`, `blob`, `format`, `manifest`, `object`, `snapshot`, `policy`, `restore`, and `upload`.
- Risks and edge cases: JSON tags are API compatibility surface; changing fields or names can break UI, CLI, or remote clients.
- Test signals: Validated indirectly by server API integration tests and client wrappers.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/serverapi/serverapi.go -->
