# sources/storage-engines/rocksdb/tools/advisor/test/input_files/test_rules.ini

## Purpose

This fixture defines a small rule set for verifying conjunction semantics in the Advisor rule parser.

## Important APIs, Types, and Functions

It includes `single-condition-false`, `multiple-conds-true`, and `multiple-conds-one-false`, with four LOG conditions and three suggestions. `l0-l1-ratio-health-check` uses a description-only suggestion.

## Control Flow

Tests load the file, trigger conditions from fixture LOG data, and assert that only the rule whose full condition list is true becomes triggered.

## State and Persistence Behavior

Static fixture only. Runtime trigger state accumulates on parsed condition/rule objects during tests.

## Dependencies and Integration Points

It is used by `TestConditionsConjunctions` with `LOG-1` and `OPTIONS-000005`.

## Risks and Test Signals

The signal is exact triggered/not-triggered rule membership. Risks are regex drift from fixture logs or names changing without updating tests.
