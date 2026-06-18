# sources/storage-engines/foundationdb/fdbcli/ConfigureCommand.cpp

Purpose: Implements the `configure` command for creating or changing database configuration, including interactive `auto` recommendations and guarded rejection of backup-worker knobs managed elsewhere.

Important APIs/types/functions: `configureCommandActor(Reference<IDatabase>, Database, tokens, LineNoise*, Future<Void>)`, `configureGenerator`, `ManagementAPI::changeConfig`, `StatusClient::statusFetcher`, `parseConfig`, `ConfigureAutoResult`, `ConfigurationResult`, and command registration via `CommandFactory configureFactory`. It uses `LineNoise` to ask for confirmation in `auto` mode.

Control flow: The actor parses optional `FORCE`, then handles `auto` by fetching status JSON either through a valid multiversion transaction special key (`\xff\xff/status/json`) or native `StatusClient::statusFetcher` fallback. It computes recommended vs current configuration, prints a comparison table, asks for confirmation, and only then proceeds. Before calling `changeConfig`, it rejects `backup_worker_enabled:=` and `range_backup_worker_enabled:=`. The returned `ConfigurationResult` is mapped to user-facing success, warnings, or errors covering invalid configs, region constraints, storage migration settings, unavailable database, experimental storage engines, and restricted backup-worker settings.

State and persistence behavior: Durable changes are performed by `ManagementAPI::changeConfig`, which writes cluster configuration metadata. `auto` mode is read-only until the user confirms. The command itself keeps only transient state and cancels warning futures once it proceeds.

Dependencies and integration points: Integrates fdbcli parsing/help/completion, status JSON schema, management configuration validation, Flow actor futures, and interactive input. Configuration text maps to core cluster configuration, TSS, proxy/log/resolver counts, storage migration, and exclusion bootstrap parameters.

Risks: This is a high-impact operational command. The `FORCE` path bypasses availability/safety checks delegated to `ManagementAPI`. `auto` relies on status JSON completeness and parse advice; manual settings can block automatic changes. Parsing uses token prefix checks for restricted backup knobs, so equivalent formatting must remain covered by tests.

Test signals: Command tests should cover no options, `FORCE`, `auto` accept/decline, unavailable status fallback, all `ConfigurationResult` mappings, restricted backup knobs, generator completions, and representative valid/invalid configuration mutations.
