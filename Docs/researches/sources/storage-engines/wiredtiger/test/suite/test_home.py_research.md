# sources/storage-engines/wiredtiger/test/suite/test_home.py

## Purpose

Covers connection home metadata APIs: `is_new`, `get_home`, and creation of `WiredTiger.basecfg` depending on `config_base`.

## Important APIs, Types, and Functions

Defines three test classes: `test_isnew`, `test_gethome`, and `test_base_config`.

## Control Flow

`test_isnew` checks a fresh connection is new, closes/reopens `.` and checks false. `test_gethome` checks default home `.` and a separately created directory. `test_base_config` asserts default base config exists, then opens another home with `config_base=false` and asserts no base config file.

## State and Persistence Behavior

Persistence is observed by closing/reopening connections and checking filesystem artifacts. The base config test opens an additional connection manually.

## Dependencies and Integration Points

Depends on `os`, `wttest`, connection open wrappers, and WiredTiger connection methods `is_new` and `get_home`.

## Risks and Maintenance Signals

The tests assume harness home is `.` and that base configuration is created during default test setup. It does not inspect base config contents.

## Test Signals

Signals are boolean API results and existence/nonexistence of `WiredTiger.basecfg`.
