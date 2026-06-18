# sources/storage-engines/wiredtiger/test/suite/test_verbose02.py

## Purpose

`test_verbose02.py` extends verbose configuration coverage to explicit verbosity levels. It verifies accepted level syntax and rejection of out-of-range levels.

## Important APIs, Types, and Functions

The class `test_verbose02` inherits `test_verbose_base`, uses flat/JSON scenarios, and defines `test_verbose_single`, `test_verbose_multiple`, and `test_verbose_level_invalid`.

## Control Flow

The single-category test opens connections with `api:1`, `api:0`, and `compact:0` through `compact:5`, performs table/cursor/compact operations, and checks whether expected verbose patterns appear. The multiple-category test exercises mixed level syntax such as `api:1,version`. Invalid tests assert `wiredtiger_open` raises for `api:-1` and `api:6`.

## State and Persistence Behavior

State is transient table activity plus captured stdout. The test repeatedly closes the default connection and opens new ones with different verbose configs.

## Dependencies and Integration Points

Depends on verbose level parsing, category-specific level filtering, `compact` verbose messages, JSON message support inherited from the base class, and `wiredtiger.WiredTigerError`.

## Risks and Edge Cases

The test assumes `api:0` currently produces no messages for its operations and that compact emits output at all tested levels. Changes in logging volume can affect expectations.

## Test Signals

Signals include output for enabled categories at valid levels, suppressed output at a non-emitting level, and parse errors for invalid levels.
