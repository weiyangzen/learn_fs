# sources/object-store/rustfs/crates/notify/src/rules/xml_config.rs

## Purpose
Parses, serializes, defaults, and validates S3 bucket notification XML configuration for queue targets.

## Important APIs, types, and functions
- `ParseConfigError` covers XML, filter, duplicate event/filter/queue, unsupported config type, ARN/target parsing, region, validation, and I/O errors.
- `FilterRule::validate` accepts only prefix/suffix and rejects `.`/`..` path segments, overlong values, backslashes, and invalid UTF-8.
- `S3KeyFilter` validates duplicate prefix/suffix rules and builds wildcard patterns.
- Custom `Deserialize` for `S3KeyFilter` handles `<Filter><S3Key><FilterRule>...` and `<FilterRuleList>` forms.
- `QueueConfig` validates events, duplicate events, filters, region, and ARN presence.
- `NotificationConfiguration` parses XML, rejects Lambda/Topic configs, validates duplicate queues, and fills default regions/xmlns.

## Control flow
`NotificationConfiguration::from_reader` deserializes XML with `quick_xml`. `set_defaults` fills missing queue ARN region and XML namespace. `validate` rejects unsupported lambda/topic entries, validates each queue, and checks duplicate `(Id, ARN)` pairs. `BucketNotificationConfig::from_xml` then consumes these validated queue configs.

## State and persistence behavior
The structs are serializable/deserializable data models. No persistence is performed here.

## Dependencies and integration points
Uses `quick_xml`, serde, `EventName`, `rustfs_targets::arn::{ARN, ArnError, TargetIDError}`, `hashbrown::HashSet`, and the local `pattern` helper. It is the XML front door for bucket notification configuration.

## Risks and edge cases
Lambda and Topic configs are explicitly unsupported even though structs exist for partial parsing. Duplicate queue detection uses `(Id, ARN)`, so identical ARN with different IDs is allowed. ARN validation requires callers to provide the current active ARN list. Unknown XML fields inside `S3Key` produce deserialization errors.

## Test signals
Covered by `config_test.rs`, which validates direct and wrapped filter rules, region defaulting, allowed ARN checks, prefix/suffix matching, capitalized filter names, and compound event expansion.
