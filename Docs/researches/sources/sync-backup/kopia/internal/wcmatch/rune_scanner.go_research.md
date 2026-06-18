<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/wcmatch/rune_scanner.go -->
# sources/sync-backup/kopia/internal/wcmatch/rune_scanner.go

- Purpose: Provides rune scanning primitives for wildcard parsing and matching.
- Important APIs/types/functions: `runeScanner`, `newRuneScanner`, `peek`, `read`, `eos`, `indexOf`.
- Control flow: Scanner stores rune slice and position, can peek relative indexes with optional lowercase conversion, read and advance, detect end, and locate a rune from current position.
- State and persistence: In-memory scanner position only.
- Dependencies and integration points: Used by `NewWildcardMatcher` and `doMatch`; depends on `unicode`.
- Risks and edge cases: Case folding only lowercases uppercase runes and does not implement full Unicode case folding equivalence.
- Test signals: Covered indirectly by `wcmatch_test.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/wcmatch/rune_scanner.go -->
