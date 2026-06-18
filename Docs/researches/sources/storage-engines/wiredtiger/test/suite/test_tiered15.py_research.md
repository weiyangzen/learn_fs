# sources/storage-engines/wiredtiger/test/suite/test_tiered15.py

## Purpose
`test_tiered15.py` verifies `session.create` behavior for the `type=` configuration when the connection is tiered and when a table explicitly disables tiered storage.

## Important APIs, Types, and Functions
The class combines `TieredConfigMixin` and `WiredTigerTestCase`. Scenario dimensions enumerate `type` values (`file`, `table`, `tier`, `tiered`, `colgroup`, `index`, `backup`) and expected tiered/non-tiered error behavior. The method under test is `test_create_type_config`.

## Control Flow
The test runs only for tiered connections. For tiered tables, it expects only `type=file` to succeed and all other types to fail with `Operation not supported`. For non-tiered tables inside a tiered connection, it creates with `tiered_storage=(name=none)` and allows some types while asserting configured errors for unsupported types. The `colgroup` non-tiered error scenario is skipped because it is expected to crash.

## State and Persistence Behavior
The test does not rely on data writes; it validates schema metadata creation constraints and the boundary between connection-level tiered defaults and table-level `name=none`.

## Dependencies and Integration Points
It integrates with schema creation, configuration validation, tiered table creation paths, and error-message assertions.

## Risks and Test Signals
The risk is inconsistent type validation when tiered storage is enabled. Signals are successful creation for allowed type combinations and exact expected exceptions for disallowed combinations.
