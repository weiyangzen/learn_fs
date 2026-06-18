# sources/storage-engines/rocksdb/tools/advisor/test/input_files/rules_err2.ini

## Purpose

This fixture verifies parse-time failure when a condition has `source=` with no source type but then receives a source-specific parameter.

## Important APIs, Types, and Functions

It defines a normal rule referencing `missing-source`, a condition with empty `source`, and normal suggestions.

## Control Flow

`RulesSpec.load_rules_from_spec` creates a base `Condition`, sees the empty source value, does not convert it to `LogCondition`, then calls the base `Condition.set_parameter` for `regex`, which raises `NotImplementedError`.

## State and Persistence Behavior

Static test fixture only.

## Dependencies and Integration Points

It is used by `TestParsingErrors.test_condition_missing_source`.

## Risks and Test Signals

The fixture depends on source being required before source-specific keys and on the base class raising the expected message. A passing test confirms malformed source handling still fails early.
