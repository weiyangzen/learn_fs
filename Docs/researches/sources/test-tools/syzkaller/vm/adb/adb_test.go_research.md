# sources/test-tools/syzkaller/vm/adb/adb_test.go

## Purpose

`adb_test.go` verifies JSON config loading and per-device config parsing for the ADB VM backend.

## Important APIs, Types, and Functions

Tests are `TestConfigParseBootService`, `TestConfigParseAllFields`, and `TestDeviceParse`. They use `config.LoadData`, `loadDevice`, `Config`, and `Device`.

## Control Flow

Each test builds raw JSON, initializes defaults where needed, loads data into config structs, and asserts expected field values. Device parsing tests cover legacy string serials and object form with `serial`, `console`, or `console_cmd`.

## State and Persistence Behavior

The tests are pure in-memory JSON parsing checks. They do not invoke ADB or mutate devices.

## Dependencies and Integration Points

They protect compatibility between manager JSON config and `adb.go` defaults, especially the newer `boot_service` option and flexible device representation.

## Risks and Test Signals

Coverage is limited to config parsing. It does not validate serial regex checks in `ctor`, ADB binary lookup, repair flow, battery parsing, or console discovery. Strong signals are default boot service preservation, explicit empty boot service behavior, all-field parsing, and legacy device string compatibility.
