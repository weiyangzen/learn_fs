# sources/storage-engines/tikv/src/coprocessor/config_manager.rs

Purpose: implements online configuration for coprocessor memory quota. `CopConfigManager` holds an `Arc<MemoryQuota>` shared with `Endpoint`.

Important APIs: `CopConfigManager::new` stores the quota handle. The `ConfigManager::dispatch` implementation removes `end_point_memory_quota` from a `ConfigChange`; if the value is not `ConfigValue::None`, it converts it to `ReadableSize` and calls `MemoryQuota::set_capacity`.

Control flow is direct and synchronous. The config subsystem invokes `dispatch`, the manager selectively handles the coprocessor memory quota key, and all other keys are ignored. State is in the shared `MemoryQuota`; no durable persistence is performed here.

Dependencies are `online_config`, `tikv_util::config::ReadableSize`, and `tikv_util::memory::MemoryQuota`. Integration point is `Endpoint::config_manager`, which boxes this manager for server configuration plumbing. Risks: key spelling must match the server config field, conversion assumes the config value carries a size, and reducing capacity can cause subsequent request admission failures. There are no local tests; endpoint memory-quota tests cover the shared quota effect.
