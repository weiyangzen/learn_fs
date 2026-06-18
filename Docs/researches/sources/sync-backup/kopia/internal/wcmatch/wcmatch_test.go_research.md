<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/wcmatch/wcmatch_test.go -->
# sources/sync-backup/kopia/internal/wcmatch/wcmatch_test.go

- Purpose: Tests wildcard matching semantics and parser error handling.
- Important APIs/types/functions: `wcCase`, `TestMatchWithBaseDir`, `TestMatch`, `TestErrorCases`, `TestCharacterClasses`, `testHelper`.
- Control flow: Table tests construct matchers with case-sensitive and case-insensitive options, normalize trailing slash directory markers, and compare expected matches. Error tests assert invalid patterns return errors and nil matchers.
- State and persistence: In-memory patterns and paths only.
- Dependencies and integration points: Directly exercises `NewWildcardMatcher` and `Match`.
- Risks and edge cases: Large table coverage is good, but performance/adversarial recursion is not measured.
- Test signals: Direct comprehensive coverage for `wcmatch`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/wcmatch/wcmatch_test.go -->
