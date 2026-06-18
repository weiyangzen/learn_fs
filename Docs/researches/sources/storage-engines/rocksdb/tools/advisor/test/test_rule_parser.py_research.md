# sources/storage-engines/rocksdb/tools/advisor/test/test_rule_parser.py

## Purpose

This is the main test suite for Advisor rule loading, validation, triggering, conjunction semantics, and parsing errors.

## Important APIs, Types, and Functions

It imports `RulesSpec`, `DatabaseOptions`, `DatabaseLogs`, and `DataSource`. Test classes are `TestAllRulesTriggered`, `TestConditionsConjunctions`, `TestSanityChecker`, and `TestParsingErrors`. The `RuleToSuggestions` map defines exact expected suggestions for triggered fixture rules.

## Control Flow

The first two classes load rules/options/log fixtures and build data-source maps, assert initial untriggered state, run triggering, and check conditions/rules. The sanity checker loads invalid rules and calls `perform_checks` expecting `ValueError`. Parsing-error tests load individual malformed INI files expecting parse-time exceptions.

## State and Persistence Behavior

The module reads fixture INI, LOG, and OPTIONS files. Runtime trigger state is held in parsed rule/condition objects.

## Dependencies and Integration Points

It exercises the interaction among `RulesSpec`, `DatabaseLogs`, `DatabaseOptions`, and the parser fixtures.

## Risks and Test Signals

Signals are exact triggered rule membership, expected suggestion names, condition truth values, and error regexes. The suite covers LOG and OPTIONS rules strongly, but time-series rule parsing/validation is mostly covered elsewhere.
