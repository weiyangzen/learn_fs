# sources/test-tools/syzkaller/dashboard/app/dungeon_test.go

Purpose: unit tests for dungeon ranking, identity, badge, class, and naming behavior.

Important tests: `TestHashEmailID` locks the 16-character hash behavior. `TestProcessPlayers` verifies badges such as Dragon Vanquisher, Necromancer, Diviner, Windwalker, Sealer, and Hydra Hunter, plus scaled Str/Wis attributes. `TestProcessKingdoms` checks score aggregation, ranking, champion/guild derivation, and guild ordering by class counts. `TestIntegrationBadges` table-tests title/commit pattern badges and negative matches. `TestTrophyLadderBadges` verifies bug-count thresholds. `TestExtractSubsystems` filters only subsystem labels. `TestPlayerRankingTieBreakers` locks score/name/email sorting. `TestMultiNameAggregation` and `TestHeroNamingLogic` verify frequent-name selection, tie handling, suffix generation, and fallback to email.

Control flow under test: tests construct in-memory `Bug`, `uiDungeonPlayer`, and `uiDungeonKingdom` maps, call `processPlayers`, `processKingdoms`, `extractSubsystems`, and `hashEmailID`, then inspect computed fields.

State and persistence behavior: no datastore or memcache is used; tests focus on deterministic transformation of in-memory bug/player/kingdom state.

Dependencies and integration points: uses `dashapi.ReproLevel` constants, dashboard `Bug`/`BugLabel` types, and `pkg/dungeon` badge/class/scaling/naming rules through the production processing functions.

Risks covered: unstable rankings, unintended badge keyword matches, broken hash IDs used in URLs, incorrect kingdom guild names, attribute scaling regressions, and contributor display-name surprises. Gaps include HTTP handlers, memcache rebuilds, access-level filtering, and real datastore bug loading.
