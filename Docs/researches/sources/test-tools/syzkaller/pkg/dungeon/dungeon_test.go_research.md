# sources/test-tools/syzkaller/pkg/dungeon/dungeon_test.go

Purpose: `dungeon_test.go` validates the deterministic behavior of the dungeon scoring and classification helpers.

Important tests: `TestResolveClass` covers empty/unknown fallback, known subsystem selection, and lexicographic tie-breaking. `TestCalculateLevel` checks level progression around level 50 and a high-score case. `TestScaleAttribute` covers logarithmic scaling and lower bound clamping. `TestIntegrationBadges` verifies representative title matches for lock, leak, hung task, null pointer, and similar badge predicates. `TestGetKingdom`, `TestGetBugXPAndDays`, `TestGetKingdomTier`, and `TestGetKingdomGuilds` cover domain mapping, XP bonuses, tier boundaries, pluralization, and sorting.

Control flow and state: tests are table-driven and use `testify/require` for exact comparisons. `time.Now` is used inside `TestGetBugXPAndDays`, but expected durations are relative to the same captured `now`, so results are deterministic.

Dependencies and integration: these tests are in-package, so they exercise exported functions plus internal details indirectly through outputs. They establish public behavioral contracts for callers that render contributor profiles.

Risks/test gaps: tests do not exhaustively cover every curated domain, class, adjective, or badge. They also do not validate display descriptions. However, they cover the main scoring thresholds and sorting/tie-breaking paths most likely to regress.
