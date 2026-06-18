<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/testutil/race.go -->
# sources/sync-backup/kopia/internal/testutil/race.go

- Purpose: Declares race-detector state for race-enabled builds.
- Important APIs/types/functions: `isRaceDetector`.
- Control flow: Declaration-only file selected by `race` build tag.
- State and persistence: Compile-time constant only.
- Dependencies and integration points: Used by testutil skip/complexity helpers.
- Risks and edge cases: Must stay complementary with `norace.go`.
- Test signals: Indirectly changes test skip/reduction behavior under `go test -race`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/testutil/race.go -->
