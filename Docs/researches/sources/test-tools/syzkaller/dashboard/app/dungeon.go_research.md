# sources/test-tools/syzkaller/dashboard/app/dungeon.go

Purpose: implements the Syzkaller Dungeon feature, a gamified dashboard view ranking bug-fixing contributors ("heroes") and email-domain groups ("kingdoms") by fixed bug activity.

Important APIs and types: UI structs `uiDungeonBadge`, `uiDungeonPlayer`, `uiDungeonKingdom`, `uiDungeonMeta`, and `uiDungeonPage` define JSON/template data. HTTP handlers `handleDungeon`, `handleHeroProfile`, and `handleKingdomProfile` serve HTML or JSON, gated to the configured dungeon namespace. `getDungeonData` reads compressed JSON from memcache or calls `fetchDungeonData`; `handleDungeonPreheat` warms cache for public/user/admin access. Helpers `addBugToPlayerMap`, `addBugToKingdomMap`, `processPlayers`, `processKingdoms`, `extractSubsystems`, `dungeonCacheKey`, `rebuildMaps`, and `hashEmailID` build ranked data.

Control flow: data generation loads fixed bugs plus open bugs that already have commits for the dungeon namespace, filters by sanitized access level, computes XP/days-open through `pkg/dungeon`, credits unique commit author emails once per bug, adds all-time and one-year entries, derives kingdoms from email domains, processes player classes/badges/attributes/levels/ranks, then aggregates kingdoms from processed heroes. Profile handlers select `era=1y` or all-time data and return 404 for missing IDs.

State and persistence behavior: source truth is datastore `Bug` entities and their `CommitInfo`, labels, repro levels, crash counts, and fix/first times. Generated dungeon pages are stored in memcache as compressed JSON for one hour by access level; maps are omitted from JSON and rebuilt after decode.

Dependencies and integration points: uses dashboard headers/templates/routing, config `DungeonNamespace`, access control, datastore bug loaders, App Engine memcache, `pkg/dungeon` scoring/class/badge logic, syzkaller hashing, compressed image utilities, and cron preheat from `cron.yaml`.

Risks: cache keys include access level but not namespace; handlers currently only allow the single dungeon namespace, so this is acceptable but would need revisiting for multiple dungeon namespaces. JSON omits internal maps, requiring `rebuildMaps` to avoid nil profile lookups after cache hits. Contributor identity is lowercased email; name aggregation and domain kingdom derivation depend on commit metadata quality. Scoring includes open bugs with commits, which may change leaderboard semantics as bugs later fix/close.

Test signals: `dungeon_test.go` covers hash stability, player/kingdom processing, badge predicates, trophy ladder thresholds, subsystem extraction, ranking tie-breakers, multi-name aggregation, and fallback naming.
