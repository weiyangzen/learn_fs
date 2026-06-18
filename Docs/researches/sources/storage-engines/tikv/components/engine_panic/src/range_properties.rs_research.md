# sources/storage-engines/tikv/components/engine_panic/src/range_properties.rs

Purpose: Panic skeleton for approximate range-size/key APIs.

Important APIs and types: `PanicEngine` implements `RangePropertiesExt` for approximate keys, approximate size, and split-key calculation on default and named CFs.

Control flow and state: All methods panic and hold no property state.

Dependencies and integration: Real engines use these APIs for region split checks and scheduling decisions.

Risks: Runtime use panics.

Test signals: No tests.
