<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/testutil/tmpdir.go -->
# sources/sync-backup/kopia/internal/testutil/tmpdir.go

- Purpose: Creates interesting temporary directories and log directories for tests, with cleanup and log dumping.
- Important APIs/types/functions: `interestingLengths`, `GetInterestingTempDirectoryName`, `TempDirectory`, `TempDirectoryShort`, `TempLogDirectory`, `dumpLogs`, `dumpLogFile`, `trimOutput`, `splitLines`.
- Control flow: Temp helpers create names with random target lengths, optionally extend paths, register cleanup that preserves failed-test artifacts, and log helpers dump bounded log output unless disabled.
- State and persistence: Creates and removes filesystem directories; may preserve logs/temp files on failures or `KOPIA_KEEP_LOGS`.
- Dependencies and integration points: Integrates `clock`, environment variables, `testing.TB`, and filesystem APIs.
- Risks and edge cases: Random path lengths can expose platform limits; preserved logs can consume disk in repeated failures.
- Test signals: Utility file; behavior is indirectly exercised by tests using temp/log helpers.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/testutil/tmpdir.go -->
