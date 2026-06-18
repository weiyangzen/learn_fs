# sources/storage-engines/wiredtiger/test/suite/test_encrypt07.py

## Purpose

Runs the general salvage regression suite against an encrypted database, ensuring salvage can locate and repair damaged encrypted pages when the test's damage marker is transformed through the encryptor.

## Important APIs, Types, and Functions

`test_encrypt07` subclasses `test_salvage01.test_salvage01`, overrides `uri`, encryption configuration, `conn_extensions`, `conn_config`, `rot13`, and `moreinit`, and re-declares parent salvage tests with tiered skips.

## Control Flow

The inherited salvage tests create data, damage files, and invoke salvage through API and process paths. This subclass loads `rotn` with key id 13 and adjusts `self.uniquebytes` in `moreinit` to the rot13-encoded byte sequence so the inherited damage logic can find the physical encrypted marker.

## State and Persistence Behavior

State and persistence are inherited from salvage: table data is written to disk, damaged, salvaged, and re-read. This subclass only changes encryption state and the damage-search bytes.

## Dependencies and Integration Points

Depends on `codecs`, `wttest`, the sibling `test_salvage01` module, and the `rotn` encryptor extension. It integrates salvage, extension loading, and inherited suite subprocess behavior.

## Risks and Maintenance Signals

The test is tightly coupled to `test_salvage01` internals, especially `uniquebytes` setup. Changes in the parent damage strategy or rotn behavior require coordinated updates.

## Test Signals

Signals are the inherited salvage API, damaged API, and process-damaged assertions running under encrypted storage; tiered mode is skipped.
