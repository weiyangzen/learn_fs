# sources/storage-engines/tikv/tests/integrations/config/test_config_client.rs

## sources/storage-engines/tikv/tests/integrations/config/test_config_client.rs

Purpose: tests online config controller update parsing, validation, dispatch to module managers, config-file rewriting, and reload from TOML file.

Important APIs: `ConfigController`, `OnlineConfig`, `ConfigManager`, `ConfigChange`, `Module::Raftstore`, `RaftstoreConfig::update`, `update`, `update_config`, `get_current`, `update_from_toml_file`, and helper `change`.

Control flow: `test_update_config` applies valid changes to schedules, raftstore threshold, and max-ts drift, then verifies validation failures, unsupported fields, unknown paths, type errors, and short names leave current config unchanged. `test_dispatch_change` registers a mock raftstore manager and checks both global current config and manager-local config update. `test_write_update_to_file` creates a TOML file with comments, commented keys, similarly named nested keys, and nested Titan config, then updates several fields and compares exact rewritten bytes. `test_update_from_toml_file` writes a raftstore config file and reloads it into the controller and registered manager.

State and persistence: temporary config files are created, rewritten, synced, and read back; mock managers store state in `Arc<Mutex<_>>`.

Dependencies and integration points: online config, TOML editor behavior, raftstore config validation, file IO. Risks include exact formatting sensitivity and validation order. Test signals are exact config equality, dispatched manager state, precise rewritten file content, and reload behavior.
