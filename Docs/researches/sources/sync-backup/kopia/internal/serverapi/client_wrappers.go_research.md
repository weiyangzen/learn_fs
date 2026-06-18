<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/serverapi/client_wrappers.go -->
# sources/sync-backup/kopia/internal/serverapi/client_wrappers.go

- Purpose: Provides typed client-side wrappers for Kopia server API endpoints.
- Important APIs/types/functions: `CreateSnapshotSource`, `Estimate`, `Restore`, `GetTask`, `UploadSnapshots`, `CancelUpload`, `CreateRepository`, `ConnectToRepository`, `DisconnectFromRepository`, `Shutdown`, `RepoStatus`, `Status`, `GetThrottlingLimits`, `SetThrottlingLimits`, `ListSources`, `ListSnapshots`, `ListPolicies`, `SetPolicy`, `ResolvePolicy`, `ListTasks`, `GetObject`, `matchSourceParameters`.
- Control flow: Each wrapper constructs a route string, allocates the expected response type, invokes `KopiaAPIClient.Get/Post/Put`, wraps errors with operation context, and returns the decoded value.
- State and persistence: Stateless wrapper layer; all persistent effects occur on the server/repository side.
- Dependencies and integration points: Integrates `apiclient`, `uitask`, throttling limits, `object.ErrObjectNotFound`, `snapshot`, and `policy`.
- Risks and edge cases: Query strings are built by string concatenation without URL escaping, so unusual host/user/path values can alter parameters.
- Test signals: Exercised by server API integration tests and helpers in `server/util_test.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/serverapi/client_wrappers.go -->
