# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ConsistencyScanInterface.h

Purpose: Declares the consistency scan worker RPC interface and the database-backed state model controlling scan configuration, range inclusion/skipping, current round stats, history, and lifetime stats.

Important APIs/types/functions: `ConsistencyScanInterface` exposes `waitFailure`, `haltConsistencyScan`, locality, and id. `HaltConsistencyScanRequest` identifies the requester and returns `Void`. `ConsistencyScanState` is a `KeyBackedClass` under `\xff/consistencyScanState`. Nested `Config` controls enablement, max read byte rate, target/min round time, minimum start version, and history retention. `RangeConfig` stores optional included/skip overlays with `apply()` and JSON conversion. `LifetimeStats` and `RoundStats` track logical bytes, replicated bytes, errors, skipped ranges, versions, timestamps, completion state, and last end key. Accessors return key-backed range/object properties and history maps. `clearStats()` clears current, lifetime, and history stats in one transaction after reading them for conflicts.

Control flow: Scan actors read `config()` and `rangeConfig()` triggers to decide whether and where to scan. They update `currentRoundStats()` and `lifetimeStats()` during execution and move completed or aborted rounds into `roundStatsHistory()`. Management paths can halt the role or clear stats; clearing reads keyspaces first to establish write conflicts, then resets stats and erases history.

State and persistence behavior: State is persisted in system keyspace through `KeyBackedTypes` and `KeyBackedRangeMap`. Config/range updates fire the class trigger; frequent stats updates intentionally do not except when resets explicitly update the trigger to prevent stale overwrite. JSON methods expose status-friendly snapshots.

Dependencies and integration points: Depends on system data, JSON spirit, commit proxy/database config/FDB types, RYW transactions, key-backed types, range maps, RPC/locality. Integrated with the consistency scan role, management/special key commands, status surfaces, and database transactions.

Risks: Trigger semantics are subtle: stats resets need explicit trigger handling or scan loops can overwrite reset values. Optional `RangeConfig` fields are overlays, so incorrect `apply()` semantics can unintentionally inherit old range settings. History retention uses versions-per-second assumptions. `clearStats()` is rare but must conflict correctly.

Test signals: Config/range key-backed read/write and trigger firing; range overlay application; JSON status output; round lifecycle from current to history; clearStats conflict behavior; halt request routing; scan restart after reset; persistence across role restart.
