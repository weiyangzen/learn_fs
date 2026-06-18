# sources/user-network-fs/gcsfuse/tools/integration_tests/rapid_appends/suites_test.go

Purpose: Defines reusable testify suite types and mount lifecycle helpers for rapid appends tests.

Important APIs/types/functions: `mountPoint` stores root, mount, test directory, and log file paths. `BaseSuite` stores flags, mount points, file name/content, and metadata-cache setting. Suite structs embed `BaseSuite`. `SetupTest`, `TearDownTest`, `setupTestDir`, `mountGcsfuse`, `unmountAndCleanupMount`, `createUnfinalizedObject`, `deleteUnfinalizedObject`, `getAppendPath`, `appendToFile`, `getNewEmptyCacheDir`, `isMetadataCacheEnabled`, and `RunTests` provide shared behavior.

Control flow: In GKE mode, setup records already-mounted paths. In GCE mode, it mounts primary and optional secondary static gcsfuse mounts. Teardown saves primary/secondary logs on failure, then either cleans GCS objects for GKE or unmounts each mount and cleans. `RunTests` filters config items by run name and expands flag strings into per-suite runs.

State/persistence: Suite state tracks current object name/content and mount paths. `appendToFile` updates expected content and syncs dual-mount writes so the other mount can observe them.

Dependencies/integration: Uses static mounting, setup artifact/log helpers, GCS client creation of unfinalized objects, and testify suite/require.

Risks/test signals: `mountGcsfuse` receives `mountPoint` by value, so updates to `mnt.testDirPath` inside it do not mutate the caller beyond initial fields already set by `setupTestDir`; tests rely on those pre-set paths. Passing suites indicate lifecycle isolation, failure log capture, and config expansion work.
