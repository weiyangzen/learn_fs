# sources/storage-engines/rocksdb/tools/advisor/test/input_files/rules_err3.ini

## Purpose

This fixture verifies parse-time failure for a suggestion that names an option but leaves `action` empty.

## Important APIs, Types, and Functions

It defines `Suggestion "missing-action"` with `option=DBOptions.max_background_flushes` and `action=`, plus a normal rule/condition/suggestion.

## Control Flow

During `RulesSpec.load_rules_from_spec`, `Suggestion.set_parameter("action", None)` detects that an option is already present and raises `ValueError`.

## State and Persistence Behavior

Static test fixture only.

## Dependencies and Integration Points

It is used by `TestParsingErrors.test_suggestion_missing_action`.

## Risks and Test Signals

The signal is an expected parse-time `ValueError`. If parser ordering changes to allow late validation only, this fixture/test contract would need adjustment.
