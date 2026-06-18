<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/flat_bucket_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/flat_bucket_test.go

Purpose: defines a testify suite for flat/non-hierarchical bucket rename behavior by combining shared filesystem setup with reusable rename test mixins.

Important APIs/types/functions: `FlatBucketTests`, `TestFlatBucketTests`, `SetT`, `SetupSuite`, `TearDownSuite`, `SetupTest`, and `TearDownTest`.

Control flow: `SetupSuite` sets `RenameDirLimit` to 20, enables implicit directories, and starts the shared `fsTest` mount. `SetupTest` seeds fake bucket objects representing directories, nested files, an implicit directory, and a separate `bar` prefix. Embedded `RenameDirTests` and `RenameFileTests` provide the actual test methods.

State and persistence: fake bucket objects are recreated before each test and removed through `fsTest.TearDown` after each test. The mount and server config live for the suite.

Dependencies and integration points: depends on `testify/suite`, `require`, the shared `fsTest`, and rename test types defined elsewhere in the repository. It targets the non-hierarchical directory rename path in `fs.go`, including object copy/delete or optional atomic rename for files.

Risks: this file's behavior depends heavily on embedded tests not listed in this subset; this setup file alone does not show the asserted rename cases. The seeded object names must match assumptions made by the shared rename suites.

Test signals: confirms the flat-bucket rename test matrix runs with implicit directories and a bounded rename directory limit, using representative explicit and implicit directory contents.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/flat_bucket_test.go -->
