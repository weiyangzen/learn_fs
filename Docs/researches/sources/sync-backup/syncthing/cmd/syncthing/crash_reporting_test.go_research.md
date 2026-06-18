# sources/sync-backup/syncthing/cmd/syncthing/crash_reporting_test.go

Purpose: unit test for panic log filtering.

Important APIs/tests: `TestFilterLogLines`.

Control flow and state: constructs sample log data with a device ID prefix, arbitrary log lines, and a panic marker. It verifies `filterLogLines` returns the first line without device prefix plus the panic section, excluding intervening logs.

Dependencies/integration: depends on `bytes.Equal` and the local filter function.

Risks and test signals: provides regression coverage for privacy filtering. It does not test HEAD/PUT upload behavior, rename-on-success, already-reported skipping, or nonstandard panic prefixes.
