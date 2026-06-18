# sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/TCInfo.h

Purpose: declares the in-memory metadata objects used by `DDTeamCollection` to represent storage servers, machines, machine teams, and server teams.

Important APIs and types: `TCServerInfo` stores server identity, desired-DC flag, collection pointer, tracker, added version, last known interface/class, store type, in-flight counters, team membership, metrics, health stats, queue timing, locality entry, promises, and AsyncVars. It exposes metric refresh, store-type refresh, desired-DC updates, team membership mutation, queue detection, space/load helpers, and cancellation. `TCMachineInfo` groups servers by machine locality. `TCMachineTeamInfo` groups machines and server teams. `TCTeamInfo` implements `IDataDistributionTeam`, exposing server interfaces/IDs, health/priority/config flags, metrics aggregation, in-flight accounting, eligibility counters, optimality, and space/load/read/CPU methods.

Control flow: team collection creates `TCServerInfo` for storage servers, groups them into machines and machine teams, builds `TCTeamInfo` server teams, then uses these objects to score candidate teams and react to health changes. Metric polling and storage stats populate server fields; team methods aggregate those values for placement decisions.

State and persistence: all fields are in-memory control-plane state. Persistent server lists, storage metadata, exclusions, and wiggle metadata are read or written by team collection/transaction code, not by these declarations.

Dependencies and integration: depends on system data, replication types, `DDTxnProcessor`, `DataDistributionTeam`, Flow refs, and arenas. `TCInfo.cpp` implements the declared behavior, and `DDTeamCollection.h` owns collections of these objects.

Risks: `TCServerInfo` exposes many mutable promises and AsyncVars, so actor lifecycle ordering matters. Methods such as `getMetrics()` assume metrics are present. `TCTeamInfo::size()` asserts server refs and IDs remain synchronized; adding servers by UID without refs is a special case that needs care.

Test signals: tests should cover server metric availability, in-flight counter updates, machine/team membership removal, team load/space/read/CPU aggregation, eligibility counters, wrong-store-type handling, and destructor cleanup of lagging zones.
