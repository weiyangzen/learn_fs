<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/testutil/testutil.go -->
# sources/sync-backup/kopia/internal/testutil/testutil.go

- Purpose: Provides common test helpers for skips, complexity decisions, leak checking, JSON parsing, reflection-driven tests, directory sizing, and type assertions.
- Important APIs/types/functions: `ProviderTest`, `SkipNonDeterministicTestUnderCodeCoverage`, `SkipTestUnlessLinux`, `SkipTestOnCIUnlessLinuxAMD64`, `ShouldReduceTestComplexity`, `ShouldSkipUnicodeFilenames`, `ShouldSkipLongFilenames`, `MyTestMain`, `MustParseJSONLines`, `RunAllTestsWithParam`, `MustGetTotalDirSize`, `EnsureType`.
- Control flow: Helpers inspect environment/runtime flags, call `testing` skip/fatal methods, run releasable verification after `m.Run`, decode JSON with unknown-field rejection, and recurse through directories.
- State and persistence: Uses environment variables and filesystem reads; `MyTestMain` exits the process with final status.
- Dependencies and integration points: Integrates `releasable`, `testify/require`, runtime metadata, and Go testing conventions.
- Risks and edge cases: Environment-driven skips can hide coverage locally; `MyTestMain` owns process exit.
- Test signals: Widely used by tests; no direct unit test in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/testutil/testutil.go -->
