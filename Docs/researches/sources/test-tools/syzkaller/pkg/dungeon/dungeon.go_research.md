# sources/test-tools/syzkaller/pkg/dungeon/dungeon.go

Purpose: `dungeon.go` turns syzkaller bug-fix history into game-like contributor metadata: kingdoms by email domain, classes by subsystem, XP/level calculations, badges, hero names, tiers, and guild summaries.

Important APIs/types/functions: `BugInfo` carries normalized bug signals. `BadgeDefinition` contains display data and a predicate. `GetKingdom`, `GetBugXPAndDays`, `ResolveClass`, `GetHeroName`, `GetBadges`, `ScaleAttribute`, `CalculateLevel`, `GetClassNameByEmoji`, `GetKingdomTier`, and `GetKingdomGuilds` are the main exported helpers. Curated maps and class lookup tables encode domain and subsystem policy.

Control flow and state: package initialization builds `classLookup` from class definitions. XP starts at 100, adds crash, age, quick-fix, and no-reproducer bonuses with caps. Class resolution picks the most frequent subsystem, with lexicographic tie-breaking. Badges are returned as fresh predicate definitions and match bug titles plus commit titles using substring or token regex checks. Guild summaries sort by count descending and then name.

Dependencies and integration: standard `math`, `regexp`, `sort`, `slices`, `strings`, and `time` are used. External callers provide already-normalized lower-case titles and subsystem counts; this package does not persist state.

Risks: classification is static and curated, so domains/subsystems drift over time. Badge predicates are text heuristics and may false-positive or miss spelling variants. Some display strings include non-ASCII icon data. Tests in `dungeon_test.go` cover tie-breaking, XP thresholds, badge matching, kingdoms, tiers, and guild sorting.
