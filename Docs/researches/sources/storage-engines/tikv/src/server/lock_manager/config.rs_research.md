# sources/storage-engines/tikv/src/server/lock_manager/config.rs

Purpose: defines pessimistic transaction lock-manager configuration, validation, backward-compatible duration decoding, and online config dispatch into running manager/detector state.

Important APIs/types/functions: `Config` contains `wait_for_lock_timeout`, `wake_up_delay_duration`, `pipelined`, `in_memory`, and in-memory lock size limits. `readable_duration_or_u64` preserves v3.x numeric millisecond compatibility. `LockManagerConfigManager` implements `ConfigManager::dispatch`.

Control flow: deserialization accepts readable duration strings or unsigned millisecond numbers for duration fields. `validate` rejects zero wait timeout. Online dispatch removes known config changes, forwards timeout changes to waiter manager and deadlock detector TTL, logs wake-up delay changes, and stores feature flags/limits into shared atomics used by storage.

State and persistence: config values are loaded from config files or online config changes; runtime state is stored in scheduler messages and atomics. This file itself does not persist anything.

Dependencies and integration: uses `online_config`, serde, `ReadableDuration`, `ReadableSize`, waiter-manager scheduler, deadlock scheduler, and atomics returned through `LockManager::get_storage_dynamic_configs`.

Risks: zero timeout is invalid because it would immediately fail waits. Dispatch ignores unknown removed keys by design but relies on online-config machinery to supply valid field names. `Ordering::Relaxed` is sufficient for config visibility but not a sequencing primitive.

Test signals: `test_config_deserialize` verifies mixed string/numeric duration parsing and readable size parsing.
