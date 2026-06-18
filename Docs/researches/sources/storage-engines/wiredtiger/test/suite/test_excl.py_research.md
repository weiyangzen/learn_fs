# sources/storage-engines/wiredtiger/test/suite/test_excl.py

## Purpose

Tests `session.create` semantics for `exclusive=true` and `exclusive=false` on file and table URIs, including tiered-storage scenario handling.

## Important APIs, Types, and Functions

Defines `test_create_excl` with scenario products over tiered storage sources and URI types, using `TieredConfigMixin`, `gen_tiered_storage_sources`, and `make_scenarios`.

## Control Flow

For each valid scenario it creates an object exclusively, verifies exclusive re-create fails, verifies non-exclusive re-create succeeds, and creates two new objects with exclusive and non-exclusive configs.

## State and Persistence Behavior

Persistence state is object metadata existence. No data rows are inserted.

## Dependencies and Integration Points

Depends on `wiredtiger`, `wttest`, tiered helper mixin, and session create configuration parsing. Tiered file URIs are skipped because unsupported.

## Risks and Maintenance Signals

The test asserts exception type but not error message. It only covers create idempotence, not drop/recreate or concurrent create races.

## Test Signals

Signals are `WiredTigerError` for exclusive existing object and success for non-exclusive existing or new objects.
