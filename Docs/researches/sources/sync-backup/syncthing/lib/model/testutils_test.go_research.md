## sources/sync-backup/syncthing/lib/model/testutils_test.go

Purpose: central test harness for model tests. It provides deterministic device IDs, default fake-folder configuration, config wrappers, model startup/cleanup, fake connection setup, ignore matcher substitution, cluster config helpers, local index event injection, config mutation helpers, and file-writing utilities.

Important APIs/types: package globals define `myID`, `device1`, `device2`, default wrappers/configs, and mocked connections. `newConfigWrapper`, `newDefaultCfgWrapper`, `newFolderConfig`, `setupModelWithConnection`, `setupModel`, `newModel`, and `testModel.ServeBackground` construct running model instances backed by sqlite temp DBs and fake filesystems. `cleanupModel` and `cleanupModelAndRemoveDir` stop services, events, DBs, and filesystem roots. `alwaysChanged` and `folderIgnoresAlwaysReload` force ignore reloads for tests. Helpers such as `basicClusterConfig`, `localIndexUpdate`, `pauseFolder`, `setFolder`, `setDevice`, `addDevice2`, `writeFile`, and `writeFilePerm` mutate model/config/filesystem state.

Control flow and state: `init` prepares a default config wrapper served in the background, sets fake device behavior, disables disk-free checks, and records a default folder config. Each test generally clones raw config into a new wrapper served under the test context, opens a temp sqlite DB, starts model and event logger goroutines, and scans folders before assertions. Cleanup cancels model and event contexts and removes config paths.

Dependencies and integration points: integrates `internal/db/sqlite`, `config`, `events`, fake `fs`, `ignore`, `protocol`, generated mocks, and random path generation. This harness is foundational for model request, folder, index, and config tests.

Risks: shared package-level defaults can leak assumptions into tests. Direct calls to model internals such as `removeFolder` and `addAndStartFolderLockedWithIgnores` make tests sensitive to internal refactors. Failure to call cleanup can leave goroutines or temp DB resources.

Test signals: not tested directly, but nearly every model test in this package depends on it; failures here cascade broadly.
