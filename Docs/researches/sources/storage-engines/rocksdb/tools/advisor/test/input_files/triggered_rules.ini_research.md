# sources/storage-engines/rocksdb/tools/advisor/test/input_files/triggered_rules.ini

## Purpose

This fixture defines a rule set expected to fully trigger against Advisor test LOG and OPTIONS fixtures.

## Important APIs, Types, and Functions

It mirrors core stall and compaction rules from `advisor/rules.ini`: memtable stalls, L0 stalls/stops, pending compaction byte stalls, and a level0-level1 option ratio health rule. Suggestions include background flush/compaction, write buffer, subcompaction, L0 trigger, and pending-byte-limit changes.

## Control Flow

`TestAllRulesTriggered` loads this file, builds log/options data sources, asserts conditions are initially unset, runs `get_triggered_rules`, and verifies every non-time-series condition and every rule is triggered with the expected suggestion names.

## State and Persistence Behavior

Static fixture only. It drives in-memory trigger dictionaries during tests.

## Dependencies and Integration Points

It depends on matching regexes in `LOG-0` and option values in `OPTIONS-000005`.

## Risks and Test Signals

The fixture is a strong smoke test for log/option rule integration but does not cover time-series sections. Main signal is exact rule-to-suggestion membership in `RuleToSuggestions`.
