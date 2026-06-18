# sources/storage-engines/wiredtiger/test/suite/test_tiered21.py

## Purpose
`test_tiered21.py` verifies that tiered storage rejects incompatible connection options, specifically `in_memory=true`.

## Important APIs, Types, and Functions
The class uses `TieredConfigMixin`, `gen_tiered_storage_sources(..., tiered_only=True)`, `open_with(additional_config)`, and assertions around `wiredtiger.WiredTigerError`.

## Control Flow
`test_options` closes the default connection and attempts to reopen with the normal tiered configuration plus `in_memory=true`, expecting an incompatibility error. `test_reconfigure` attempts `conn.reconfigure('in_memory=true')` on an existing tiered connection and expects an unknown configuration key error.

## State and Persistence Behavior
No data is created. The test validates configuration state transitions at open and reconfigure time. The persistent behavior is negative: an in-memory engine cannot be combined with tiered storage's durable object model.

## Dependencies and Integration Points
It integrates with connection-open validation, connection reconfigure validation, tiered connection scenario setup, and error-message matching.

## Risks and Test Signals
The risk is accepting unsupported option combinations and later failing in less clear paths. Signals are precise failures for open-time incompatibility and reconfigure-time invalid key handling.
