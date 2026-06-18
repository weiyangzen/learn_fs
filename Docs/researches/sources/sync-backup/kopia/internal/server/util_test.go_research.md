<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/util_test.go -->
# sources/sync-backup/kopia/internal/server/util_test.go

- Purpose: Provides test helper functions for server API tests.
- Important APIs/types/functions: `mustCreateSource`, `mustSetPolicy`, `mustListSources`, `mustGetTask`, `mustListTasks`, `mustGetLatestTask`, `waitForTask`.
- Control flow: Helpers wrap typed `serverapi` calls with `testlogging.Context`, assert no error, and return decoded source/task data; `waitForTask` polls until completion or timeout.
- State and persistence: No persistent state; uses remote server API state, source policy manifests, and UI task state created by tests.
- Dependencies and integration points: Integrates `apiclient`, `serverapi`, `testlogging`, `uitask`, `snapshot`, `policy`, and `clock`.
- Risks and edge cases: Polling sleeps on real time and fails the test with the last task state when timeout is reached.
- Test signals: Supports broader server test files; it has no top-level `Test...` function itself.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/util_test.go -->
