# sources/storage-engines/foundationdb/fdbcli/FileConfigureCommand.cpp

Purpose: Implements `fileconfigure`, which reads a JSON configuration file, validates it against the cluster configuration schema, converts it to a configure string, and applies it through the management API.

Important APIs/types/functions: `fileConfigureCommandActor(Reference<IDatabase>, filePath, isNewDatabase, force)`, `readFileBytes`, `json_spirit::read_string`, `JSONSchemas::clusterConfigurationSchema`, `schemaMatch`, `DatabaseConfiguration::configureStringFromJSON`, `ManagementAPI::changeConfig`, and `ConfigurationResult`.

Control flow: The actor reads up to 100000 bytes from the file, parses JSON, requires a top-level object, loads and applies the schema, converts the JSON to a configure string, prepends `new` for new database creation or removes the leading space otherwise, rejects restricted backup-worker settings, then calls `changeConfig`. It maps configuration result variants to fileconfigure-specific errors/warnings and success messages.

State and persistence behavior: Local file input is read only. Persistent changes are cluster configuration changes made through `ManagementAPI`. The command has no local output files or cache.

Dependencies and integration points: Integrates fdbcli command help, fdbclient schema validation, database configuration serialization, and the same management configuration machinery used by `configure`.

Risks: The 100000-byte read limit must be sufficient for supported config JSON. Restricted setting detection uses substring search on serialized configure text and may depend on formatting. Some newer `ConfigurationResult` variants handled by `configure` are not present here, so enum expansion can hit `ASSERT(false)` until updated.

Test signals: Cover invalid JSON, non-object JSON, schema mismatch messages, conversion exceptions, `new` vs existing config string construction, restricted backup-worker settings, force/unavailable failures, and every handled `ConfigurationResult`.
