# sources/storage-engines/rocksdb/tools/advisor/test/input_files/rules_err4.ini

## Purpose

This fixture verifies section-header validation when a section type lacks a quoted section name.

## Important APIs, Types, and Functions

It ends with `[Suggestion]` followed by valid-looking suggestion keys.

## Control Flow

`RulesSpec.load_rules_from_spec` classifies `[Suggestion]` as a suggestion section, then `IniParser.get_section_name` fails because there is no quoted name token and raises `ValueError`.

## State and Persistence Behavior

Static test fixture only.

## Dependencies and Integration Points

It is used by `TestParsingErrors.test_section_no_name`.

## Risks and Test Signals

The test protects the DSL requirement that every Rule, Condition, and Suggestion section has a stable quoted identifier.
