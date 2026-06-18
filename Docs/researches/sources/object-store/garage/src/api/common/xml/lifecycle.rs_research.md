## sources/object-store/garage/src/api/common/xml/lifecycle.rs

Purpose: serializes/deserializes S3 lifecycle XML and validates/converts it into Garage lifecycle rules.

Important APIs/types/functions: `LifecycleConfiguration`, `LifecycleRule`, `Filter`, `Expiration`, `AbortIncompleteMpu`; conversion methods `validate_into_garage_lifecycle_config`, `from_garage_lifecycle_config`, `validate_into_garage_lifecycle_rule`, `Filter::validate_into_garage_lifecycle_filter`, and `Expiration::validate_into_garage_lifecycle_expiration`.

Control flow: rule status maps `Enabled`/`Disabled` to boolean. Filters may contain one simple condition or multiple conditions wrapped in a non-nested `And`; invalid combinations return string errors. Expiration accepts exactly one of `Days` or `Date`, validating dates through the model helper. Reverse conversion emits `And` when multiple filter conditions exist.

State/persistence: no direct persistence; converted `GarageLifecycleRule` values are stored in bucket configuration by callers.

Dependencies/integration: used by S3 lifecycle handlers. Depends on `garage_model::bucket_table` lifecycle types and XML helper wrappers.

Risks: errors are `&'static str`, so callers must map them into API errors consistently. Numeric casts from `i64` to unsigned/usize can accept negative XML values incorrectly if upstream validation does not reject them. Nested `And` is explicitly rejected.

Test signals: local test covers XML round-trip, validation into Garage rules, and conversion back to equivalent XML.
