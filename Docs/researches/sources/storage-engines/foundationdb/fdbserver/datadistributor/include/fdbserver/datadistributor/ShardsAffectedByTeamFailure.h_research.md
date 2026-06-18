# sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/ShardsAffectedByTeamFailure.h

Purpose: declares the shard/team failure index used by DD to know which shards are affected by a failed or degraded team. It also serves as the mock key-server mapping.

Important APIs and types: `ShardsAffectedByTeamFailure::Team` is a sorted vector of server UIDs plus a primary flag, with comparison, equality, membership, removal, and stringification. Public methods expose shard counts, shards for a team, teams for a key/range, source-server extraction, shard definition, movement, raw movement, move finish, assignment, consistency checking, failed-server removal, range iteration, and `restartShardTracker` signaling.

Control flow: the intended mutation pipeline is `defineShard()` to adjust boundaries, `moveShard()` to set destination teams while preserving previous sources, and `finishMove()` to clear previous sources after completion. `assignRangeToTeams()` wraps that full pipeline for direct assignment.

State and persistence: private state consists of a `KeyRangeMap` from shard ranges to current/previous teams, a secondary set from team to ranges, and per-server shard counts. It is in-memory only and must be rebuilt or updated by DD logic.

Dependencies and integration: depends on Flow refs/random, FDB key/range types, and `KeyRangeMap`. It is used by team collection, tracker, transaction processor, data distribution startup, and mock global state.

Risks: `Team` requires sorted server vectors; unsorted input breaks map ordering and equality expectations. The secondary indexes are manually maintained. `CheckMode::ForceNoCheck` can hide corruption, while `ForceCheck` can be expensive.

Test signals: test coverage should target overlapping move semantics, previous-source retention, server count changes, failed-server removal, team ordering with `primary`, and consistency-check behavior.
