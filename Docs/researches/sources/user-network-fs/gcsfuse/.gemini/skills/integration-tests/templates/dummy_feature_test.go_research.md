## sources/user-network-fs/gcsfuse/.gemini/skills/integration-tests/templates/dummy_feature_test.go

Purpose: Template for a feature integration test suite in the gcsfuse repository.

Important APIs/types/functions: `dummyFeatureSuite` embeds `suite.Suite` and carries per-run `flags` plus `testDir`. `SetupSuite` mounts gcsfuse with `testEnv.mountFunc`; `TearDownSuite` unmounts; `SetupTest` creates a randomized test directory; `TearDownTest` saves logs on failure. `TestScenarioExample` demonstrates Arrange/Act/Assert using integration-test `operations` helpers. `TestDummyFeatureSuite` dispatches either a single GKE-mounted run or multiple local flag-set runs.

Control flow: suite setup mounts, each test creates a target directory/file, reads content, asserts content and OS stat visibility, then teardown records logs. Local runs call `setup.BuildFlagSets` and run the same suite once per flag configuration.

State and persistence: creates directories and files under the test bucket/mount. Cleanup is mostly delegated to package-level `TestMain` in `setup_test.go`; failed tests may persist copied logs.

Dependencies and integration points: depends on shared `testEnv`, `setup`, `operations`, `testify/assert`, and `testify/suite`. It is meant to be copied and renamed for real test packages.

Risks: package/type names are placeholders and must be changed. Because the suite object is reused while `flags` mutates in the loop, parallelization would be unsafe unless each run gets an isolated suite instance. GKE and local paths differ, so tests should avoid assumptions about mount layout.

Test signals: the example covers create/read/stat through gcsfuse and ensures the test harness can run static, dynamic, only-dir, and GKE modes when paired with the template setup.
