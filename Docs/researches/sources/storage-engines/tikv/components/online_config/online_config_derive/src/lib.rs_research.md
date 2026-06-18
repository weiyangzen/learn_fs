# sources/storage-engines/tikv/components/online_config/online_config_derive/src/lib.rs

## Purpose
This proc macro derives `online_config::OnlineConfig` for named, non-generic structs. It generates diff, update, type-description, and hidden-field-aware encoder code.

## Important APIs, Types, and Functions
- `config` is the `#[proc_macro_derive(OnlineConfig, attributes(online_config))]` entry point.
- `generate_token` validates generics, builds a stable-ish encoder type name with a hash, gathers fields, and emits the trait impl plus encoder struct.
- `update` generates logic for normal fields, `Option<T>` fields, and `#[online_config(submodule)]` fields.
- `diff` generates field-by-field differences as `ConfigChange`.
- `typed` generates a map describing current field value types, using `ConfigValue::Skip` for skipped or hidden fields.
- `encoder` generates a serde-serializable borrowed encoder that omits hidden fields and recursively encodes submodules.
- Attribute parsing recognizes `skip`, `hidden`, and `submodule`.

## Control Flow
The macro only accepts named-field structs without generics or where clauses. Hidden and skip fields are not updated or diffed; hidden fields are also omitted from encoder output. Submodules call `OnlineConfig` recursively. Option fields use `ConfigValue::None` to clear the option, otherwise `TryInto` to set `Some`.

## State and Persistence Behavior
The generated `update` mutates the config instance in place. The generated encoder only borrows the original config and does not own state. The generated type map can be used by config tooling to understand mutable and skipped fields.

## Dependencies and Integration Points
The macro emits references to a crate named `online_config`, serde derives, and `std::convert::TryInto`. It preserves only serde attributes on the generated encoder, which is critical for kebab-case and field rename behavior.

## Risks
The derive is not usable on generic structs or tuple/unit structs. Field names in diffs are Rust field identifiers, not serde-renamed names, while encoder serialization respects serde attributes; callers must not confuse update keys with serialized config keys. `is_option_type` is path-string based and only recognizes common `Option` paths.

## Test Signals
Runtime tests in `online_config` cover updates, skipped fields, submodules, hidden encoder output, optional fields, and enum conversion failures.
