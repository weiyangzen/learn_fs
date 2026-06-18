# sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/DataDistributionTeam.h

Purpose: defines the abstract team interface and team-selection request object used by DD to choose source/destination teams for relocation, read balancing, storage-queue balancing, and bulk load.

Important APIs and types: `data_distribution::EligibilityCounter` tracks counts for `LOW_CPU` and `LOW_DISK_UTIL` eligibility bits. `IDataDistributionTeam` declares metrics, membership, health, priority, in-flight, space, read-load, CPU, store-configuration, and identity methods. Boolean params describe team-selection preferences. `TeamSelect` distinguishes normal selection, complete-source preference, and true-best selection. `GetTeamRequest` packages selection flags, source sets, optional key range, penalty, and reply promise.

Control flow: callers fill `GetTeamRequest`, send it to a team collection, and receive an optional team plus a boolean status. `lessCompare()` ranks candidate teams using read-load comparison when read balancing is requested, otherwise disk-load comparison; load direction flips when lower utilization is preferred. `fromGetTeamRequest()` lets eligibility counters derive combined conditions.

State and persistence: no persistence. `GetTeamRequest` is transient actor-message state. Team implementations such as `TCTeamInfo` provide the backing state and reference counting.

Dependencies and integration: depends on `StorageServerInterface`, `UID`, Flow promises, and `GetTeamRequest` consumers in `DDTeamCollection`. `TCTeamInfo` implements `IDataDistributionTeam`.

Risks: `TeamSelect::operator==` is non-const, which can be inconvenient in const contexts. Comparator behavior mixes read and disk signals; incorrect preference flags can select the opposite end of utilization. `GetTeamRequest` has many booleans, so constructor defaults and call-site readability are important.

Test signals: tests should cover comparator direction for disk/read balancing, `findTeamByServers`, complete-source selection, bulk-load selection, storage-queue awareness, eligibility counts, and `getDesc()` diagnostics.
