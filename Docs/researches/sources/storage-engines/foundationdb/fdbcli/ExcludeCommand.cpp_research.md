# sources/storage-engines/foundationdb/fdbcli/ExcludeCommand.cpp

Purpose: Implements `exclude`, allowing operators to exclude or mark failed servers/localities, list current exclusions and in-progress exclusions, wait for safe data movement, and warn about coordinators or missing workers.

Important APIs/types/functions: `excludeCommandActor`, private helpers `excludeServersAndLocalities`, `getExcludedServers`, `getExcludedLocalities`, `getFailedServers`, `getFailedLocalities`, `getInProgressExclusion`, `checkForExcludingServers`, and `checkForCoordinators`. Special ranges include `excludedServersSpecialKeyRange`, `failedServersSpecialKeyRange`, `excludedLocalitySpecialKeyRange`, `failedLocalitySpecialKeyRange`, force-option keys, and `exclusionInProgressSpecialKeyRange`.

Control flow: With no arguments, the actor lists excluded servers/localities, failed servers/localities, and in-progress process exclusions. With arguments, it fetches workers and storage-server interfaces, parses `FORCE`, `no_wait`, `failed`, locality selectors, and `AddressExclusion`s, expands localities to address exclusions for wait/warning logic, writes requested exclusion/failed keys with optional force marker, optionally waits until in-progress exclusions no longer overlap the requested set, then prints per-address success/in-progress/missing warnings and coordinator warnings.

State and persistence behavior: Persists special-key-backed exclusion and failed metadata. `failed` semantics can cause the cluster to forget state and restore lost ranges to empty, so it can be data-loss inducing. No local persistence.

Dependencies and integration points: Integrates with worker discovery (`getWorkers`), storage server interfaces, locality expansion helpers, coordinator special keys, management special-key failure messages, and data distribution movement that clears in-progress exclusions.

Risks: High operational risk, especially `failed` and `FORCE`. Locality selectors with no matches are still written and warned afterward. Safety depends on special-key API checks unless forced. The in-progress wait polls rather than watches. Coordinator parsing only handles network addresses from the coordinator process key, not hostnames.

Test signals: Cover list output for all four exclusion classes, address/locality parsing, TLS suffix warning, force markers, failed mode, no-wait, missing worker warnings, in-progress wait and overlap logic, coordinator warnings, no-match locality warnings, and special-key failure message customization.
