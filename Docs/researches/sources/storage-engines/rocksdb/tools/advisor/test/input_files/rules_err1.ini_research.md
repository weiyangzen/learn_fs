# sources/storage-engines/rocksdb/tools/advisor/test/input_files/rules_err1.ini

## Purpose

This fixture contains intentionally invalid Advisor rules used to verify section validation failures after parsing succeeds.

## Important APIs, Types, and Functions

It defines rules missing suggestions or conditions, conditions missing options, expressions, or regexes, and suggestions missing option/description fields. It is consumed by `TestSanityChecker` in `test_rule_parser.py`.

## Control Flow

Tests parse the file with `RulesSpec.load_rules_from_spec`, fetch the dictionaries, and call `perform_checks()` on selected rules, conditions, and suggestions expecting `ValueError` messages.

## State and Persistence Behavior

It is static test input and has no runtime persistence.

## Dependencies and Integration Points

It depends on exact section names such as `missing-suggestions`, `missing-conditions`, `missing-regex`, `missing-options`, `missing-expression`, `missing-option`, and `missing-description`.

## Risks and Test Signals

Risks are fixture drift from parser error messages and accidentally making an invalid section valid. Signals are the `assertRaisesRegex` checks in `TestSanityChecker`.
