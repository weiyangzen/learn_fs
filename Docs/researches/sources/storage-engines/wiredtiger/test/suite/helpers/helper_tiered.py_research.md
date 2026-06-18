# sources/storage-engines/wiredtiger/test/suite/helpers/helper_tiered.py

Purpose: helper module for tiered storage test scenarios and connection/extension configuration.

Important APIs and control flow: top-level functions supply storage-source auth tokens, bucket names, connection config strings, shared-tiered config strings, row-check helper `get_check`, and scenario lists from `gen_tiered_storage_sources()`. `TieredConfigMixin` detects tiered/shared scenarios, builds `conn_config`, creates local bucket directories, appends `tiered_storage=(...)` config, loads storage source extensions with optional config, and marks extensions skip-if-missing for nonlocal or Windows environments.

State and persistence behavior: creates bucket directories under the test home for local `dir_store` scenarios. Connection configs enable tiered storage and statistics. The placeholder `download_objects()` does nothing by default.

Dependencies and integration points: depends on `wiredtiger`, `os`, test extension-list API, and scenario attributes such as `ss_name`, `bucket`, `bucket_prefix`, and `auth_token`.

Risks: only `dir_store` is configured in the scenario list. Some config-builder helpers return strings with open parentheses/trailing comma fragments intended to be composed by callers, so misuse can produce malformed config. Windows skips extension loading.

Test signals: tiered tests verify object movement/visibility using generated scenarios, bucket setup, and extension loading.
