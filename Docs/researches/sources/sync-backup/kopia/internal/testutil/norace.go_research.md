<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/testutil/norace.go -->
# sources/sync-backup/kopia/internal/testutil/norace.go

- Purpose: Declares race-detector state for non-race builds.
- Important APIs/types/functions: `isRaceDetector`.
- Control flow: Declaration-only file selected by `!race` build tag.
- State and persistence: Compile-time constant only.
- Dependencies and integration points: Used by testutil skip/complexity helpers.
- Risks and edge cases: Must stay complementary with `race.go`.
- Test signals: Indirectly affects tests that call `ShouldReduceTestComplexity` or skip helpers.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/testutil/norace.go -->
