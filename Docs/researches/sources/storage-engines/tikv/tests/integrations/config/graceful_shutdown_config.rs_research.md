# sources/storage-engines/tikv/tests/integrations/config/graceful_shutdown_config.rs

## sources/storage-engines/tikv/tests/integrations/config/graceful_shutdown_config.rs

Purpose: regression coverage for the server graceful shutdown timeout config.

Important APIs: `TikvConfig::default`, `server.graceful_shutdown_timeout`, `ReadableDuration::secs`, and `toml::Value::try_from`.

Control flow: one test asserts the default timeout is 20 seconds. Another mutates it to 25 seconds, serializes only the server config to TOML, and asserts the serialized table contains `graceful-shutdown-timeout`.

State and persistence: purely in-memory config serialization, no file IO.

Dependencies and integration points: TiKV config serde and TOML field naming. Risks are field rename or serde skip behavior. Test signal is default duration equality and presence of the TOML key.
