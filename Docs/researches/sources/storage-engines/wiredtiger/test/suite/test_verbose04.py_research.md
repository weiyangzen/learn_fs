# sources/storage-engines/wiredtiger/test/suite/test_verbose04.py

## Purpose

`test_verbose04.py` tests the special verbose category `all` and the public category enumeration API. It is skipped under tiered storage because tiered output changes the expected logs.

## Important APIs, Types, and Functions

The class derives from `test_verbose_base`, builds `all_verbose_categories` from `wiredtiger.wiredtiger_get_verbose_categories`, and defines `test_verbose_categories`, `test_verbose_all`, and `test_verbose_multiple`.

## Control Flow

`test_verbose_categories` compares returned categories with `WT_VERB_*` attributes except default/count sentinels. `test_verbose_all` opens connections with `all` at levels 0 through 5 and triggers table/cursor/compact operations. `test_verbose_multiple` combines `api`, `all`, and `version` to ensure category filtering follows precedence expectations.

## State and Persistence Behavior

The test creates short-lived tables to generate output and inspects captured stdout. No durable data state is validated beyond successful operations.

## Dependencies and Integration Points

Depends on category enumeration, `WT_VERB_NUM_CATEGORIES`, `all` parsing, level filtering, inherited JSON/flat validation, and compaction verbosity.

## Risks and Edge Cases

The category set must track the Python module constants exactly. The multiple-category expectation removes API/version from the all set and is sensitive to precedence semantics.

## Test Signals

Signals are category list equality, output matching any enabled verbose category under `all`, and correct suppression/selection when `all` is combined with explicit categories.
