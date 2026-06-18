# sources/storage-engines/foundationdb/fdbserver/datadistributor/ShardsAffectedByTeamFailure.cpp

Purpose: implements the DD-side index that maps shards to current and previous teams, teams to affected shards, and storage servers to shard counts. Team trackers use it to identify which shards must be relocated when teams degrade, while mock DD uses it as the key-server mapping.

Important APIs and functions: lookup methods include `getShardsFor()`, `hasShards()`, `getNumberOfShards(UID|Team)`, `getTeamsForFirstShard()`, `getTeamsFor()`, `getSourceServerIdsFor()`, `getAllRanges()`, and `intersectingRanges()`. Mutation methods include `defineShard()`, `moveShard()`, `rawMoveShard()`, `finishMove()`, `assignRangeToTeams()`, `removeFailedServerForRange()`, and private `insert()/erase()` helpers.

Control flow: `defineShard()` splits/defines boundaries, collects existing current and previous teams, installs the new range, then re-inserts team-to-shard index rows for affected ranges. `moveShard()` changes ownership without changing boundaries; exact-contained shards are rewritten with destination teams and accumulated previous teams, while intersecting partial shards are unioned so failure reactions do not lose old team information. `finishMove()` clears previous-team vectors after a move completes. `rawMoveShard()` directly writes source/destination state for exact shard ranges. `assignRangeToTeams()` performs define, move, and finish in sequence.

State and persistence: the authoritative in-memory map is `KeyRangeMap<pair<vector<Team>, vector<Team>>> shard_teams`, where first is current source or destination and second is previous sources for in-flight shards. `team_shards` is a secondary set keyed by team and range. `storageServerShards` counts shard membership by server UID. There is no durable storage here; callers rebuild it from system keys or mock state.

Dependencies and integration: depends on `KeyRangeMap`, Flow reference counting, `UID`, `KeyRange`, and sorted `Team` semantics. It feeds `DDTeamCollection` team trackers, `DataDistributionTracker`, `DDTxnProcessor` removal flows, and `MockGlobalState` source/destination checks.

Risks: consistency depends on every mutation keeping `shard_teams`, `team_shards`, and `storageServerShards` synchronized. `getTeamsFor()` indexes by exact key in `KeyRangeMap`, so callers must understand range-map semantics. `removeFailedServerForRange()` mutates vectors in place while updating secondary indexes; missed erase/insert pairing would corrupt shard counts. Expensive `check()` is gated by validation knobs or force mode, so production paths may not catch drift immediately.

Test signals: no tests in this implementation file, but the mock global-state tests exercise `assignRangeToTeams()`, key-location lookups, and source/destination queries. Good focused tests would cover overlapping moves, queued splits/merges, server removal from both current and previous team vectors, and forced `check()` failures.
