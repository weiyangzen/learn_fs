# sources/object-store/rustfs/crates/targets/src/arn.rs

## Purpose
Defines target IDs and ARN representations for notification targets, including serde conversion and parsers.

## Important APIs and Types
`TargetID` stores `id` and `name`, formats as `id:name`, parses exactly one colon with `splitn(2, ':')`, serializes as a string, and can convert to an `ARN` for a region. `TargetIDError` reports invalid `ID:Name` strings.

`ARN` stores target ID, region, service, and partition. `ARN::new` uses default service/partition from `rustfs_config::notify`. `to_arn_string` formats with `ARN_PREFIX`. `ARN::parse` strictly accepts strings starting with `ARN_PREFIX` and exactly six colon-separated tokens, rejecting empty target id/name and returning `TargetError::InvalidARN`. `Display` emits `arn:partition:service:region:id:name`. `FromStr` is more general: it accepts any `arn` prefix with at least six tokens and rejoins remaining tokens into the name. Empty-string deserialization yields an empty default ARN.

## Control Flow and State
No persistence beyond serde string form. Parsers are synchronous and allocate token vectors.

## Integration Points
Uses `rustfs_config::notify::{ARN_PREFIX, DEFAULT_ARN_PARTITION, DEFAULT_ARN_SERVICE}`, `crate::TargetError`, serde traits, and `thiserror`. Target configuration and event routing likely use these IDs to match configured notification targets.

## Risks
There are two parsing paths with different strictness: `ARN::parse` requires exactly six tokens and RustFS prefix, while `FromStr` allows names containing colons and arbitrary partition/service. `to_arn_string` and `Display` may diverge if `ARN_PREFIX` changes from the displayed partition/service composition. `TargetID::from_str` permits empty id or name if a colon exists.

## Test Signals
No tests in this file. Behavior is likely exercised indirectly by target config tests elsewhere.
