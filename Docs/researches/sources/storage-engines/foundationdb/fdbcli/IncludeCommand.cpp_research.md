# sources/storage-engines/foundationdb/fdbcli/IncludeCommand.cpp

Purpose: Implements `include`, clearing prior excluded or failed server/locality entries so processes or localities may rejoin the database.

Important APIs/types/functions: `includeCommandActor`, private `include`, `includeServers`, `includeLocalities`, `AddressExclusion`, `LocalityData::ExcludeLocalityPrefix`, and the special-key ranges exported by `ExcludeCommand.cpp`.

Control flow: The actor requires at least one argument after `include`. The helper parses `all`, `failed`, locality selectors, and address exclusions. `all` constructs an invalid `AddressExclusion` sentinel to clear the entire failed or excluded server range and clears the whole locality range. Otherwise it clears specific address keys and/or locality keys. Whole-machine address inclusion also clears port-level exclusions for that IP using the `IP:` to `IP;` key range. Errors for invalid tokens include a TLS suffix hint.

State and persistence behavior: Persists by clearing special keys under excluded/failed server and locality ranges. It does not validate that cleared entries existed. No local state.

Dependencies and integration points: Shares exclusion special key contracts with `ExcludeCommand.cpp` and affects data distribution recruitment behavior. Uses special-key writes and normal transaction retry loops.

Risks: `all` plus `failed` clears all failed entries, which may reintroduce processes intended to remain failed. The local `versionKey` variables are unused. Clearing whole-machine port ranges relies on string ordering around `:` and `;`, which is documented in comments and should remain tested.

Test signals: Cover clearing specific IP, IP:port, whole-machine plus port-level entries, localities, all, failed variants, invalid token/TLS suffix handling, idempotent clears, and transaction retry.
