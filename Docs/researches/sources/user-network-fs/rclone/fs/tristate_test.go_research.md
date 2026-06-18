# sources/user-network-fs/rclone/fs/tristate_test.go

## Purpose
This file validates `Tristate` as both a nullable boolean and a rclone flag/config value.

## Important APIs, Flow, Risks, and Signals
Compile-time assertions confirm `*Tristate` satisfies `Flagger` and `Tristate` satisfies `FlaggerNP`. `TestTristateString` covers unset and valid rendering. `TestTristateSet` covers unset spellings, booleans, numeric booleans, uppercase unset, and invalid input. `TestTristateScan` verifies `fmt.Sscan` integration. JSON tests cover `null`, booleans, invalid identifiers, empty input, and marshal output.

The tests instantiate fresh values per case and assert both errors and final fields. Dependencies are `encoding/json`, `fmt`, `testing`, and `testify`. The suite protects command-line parsing, config JSON behavior, and the invariant that `Valid` controls interpretation more than `Value`.
