# sources/storage-engines/tikv/components/online_config/src/lib.rs

## Purpose
`online_config` defines the runtime data model and trait for comparing, applying, serializing, and describing online configuration changes.

## Important APIs, Types, and Functions
- `ConfigChange = HashMap<String, ConfigValue>`.
- `ConfigValue` represents typed values: duration, size, numeric primitives, bool, string, module, schedule strings, skip, and none.
- `Display`/`Debug` make `ConfigValue` user-visible; `From` impls create values from primitive types and module maps; selected `From<ConfigValue>` impls extract values and panic on mismatches.
- `OnlineConfig<'a>` requires associated `Encoder`, `diff`, `update`, `get_encoder`, and `typed`.
- `ConfigManager` provides a `dispatch(ConfigChange)` hook for applying changes.

## Control Flow
Most runtime behavior is supplied by the derive macro. The trait contract is that `diff` produces a `ConfigChange`, `update` applies compatible changes, `get_encoder` returns a serde encoder with hidden fields omitted, and `typed` reports field types/skip markers. Tests exercise generated behavior through sample configs.

## State and Persistence Behavior
This crate does not own global state. Consumer configs are mutated in place through `update`; encoders borrow configs for serialization. `ConfigValue::None` is a sentinel for clearing optional fields, while `Skip` marks non-updatable fields in type descriptions.

## Dependencies and Integration Points
The crate re-exports `online_config_derive::*`, uses `chrono` aliases for schedules, and depends on serde for encoder serialization. Many TiKV components use `ConfigManager` implementations to apply runtime config changes.

## Risks
Extractor `From<ConfigValue>` impls panic on type mismatch; safer callers should prefer `TryFrom` where available. `Display` for module/schedule values is debug-like and not a stable machine format. Derived update keys use Rust field names, which may differ from serde names in serialized config files.

## Test Signals
Tests cover update/diff behavior, no-op updates, skipped fields, submodule updates, hidden fields omitted from encoder output, serde output with renamed fields, and enum conversion including invalid values.
