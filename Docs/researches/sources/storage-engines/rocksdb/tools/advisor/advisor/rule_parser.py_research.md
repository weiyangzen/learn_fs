# sources/storage-engines/rocksdb/tools/advisor/advisor/rule_parser.py

## Purpose

`rule_parser.py` implements the Advisor rule DSL: rules combine conditions and suggestions, conditions bind to log/options/time-series sources, and `RulesSpec` loads a rules file and determines which rules are triggered.

## Important APIs, Types, and Functions

Core classes are `Section`, `Rule`, `Suggestion`, `Condition`, `LogCondition`, `OptionCondition`, `TimeSeriesCondition`, and `RulesSpec`. `Suggestion.Action` supports `set`, `increase`, and `decrease`. Important methods include `perform_checks`, `set_parameter`, `Rule.is_triggered`, `Rule.get_overlap_timestamps`, `RulesSpec.load_rules_from_spec`, `trigger_conditions`, `get_triggered_rules`, and `print_rules`.

## Control Flow

`RulesSpec.load_rules_from_spec` scans an INI-like file, creates section objects, converts base `Condition` objects to source-specific subclasses when it sees `source`, and assigns parameters. `perform_section_checks` validates all sections. Triggering first asks each data source to set condition triggers, then tests each rule as a conjunction. Rules with `overlap_time_period` require two time-series conditions with nearby trigger epochs.

## State and Persistence Behavior

State lives in dictionaries of rule, condition, and suggestion objects. Trigger state is mutable on conditions and rules and is reset only by reparsing/recreating objects.

## Dependencies and Integration Points

It depends on `re`, `abc`, `Enum`, `DataSource`, `NO_COL_FAMILY`, `TimeSeriesData`, and `IniParser`. It is central to the Advisor CLI, optimizer, fixtures, and tests.

## Risks and Test Signals

Risks include source needing to be the first condition parameter, `Enum` key errors for bad action/behavior names, trigger state reuse, unchecked references to unknown condition/suggestion names, and an index-order bug risk in overlap scanning. Tests cover all triggered sample rules, conjunction behavior, missing required fields, missing source/action, and section header parse errors.
