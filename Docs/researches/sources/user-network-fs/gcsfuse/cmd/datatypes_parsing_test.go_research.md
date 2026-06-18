# sources/user-network-fs/gcsfuse/cmd/datatypes_parsing_test.go

## Purpose
`datatypes_parsing_test.go` verifies that every supported parameter data type can be parsed through both CLI flags and YAML config files. It is a compatibility suite for legacy single-hyphen flags, standard double-hyphen flags, short built-in help/version flags, and custom cfg text unmarshalling.

## Important APIs And Test Structure
`TestCLIFlagPassing` builds `newRootCmd`, uses `convertToPosixArgs`, executes with synthetic args, and checks captured config fields for ints, floats, strings, booleans, durations, octal permissions, repeated/comma-separated string slices, log severity, protocol, resolved paths, profile, and local socket address. `TestConfigPassing` reads YAML files from `cmd/testdata` for the same data families. `TestPredefinedFlagThrowNoError` verifies help/version invocations with `--help`, `-help`, `-h`, `--h`, `--version`, `-version`, `-v`, and `--v`.

## Control Flow And State
The tests execute command parsing but use a fake mount function, so no filesystem mount occurs. CLI cases append a dummy mount argument to satisfy command arity. Config-file cases load from testdata and assert final parsed values. Path resolution may depend on process environment, but expected cases use stable absolute paths such as `/home` or config testdata.

## Dependencies And Integration
The suite integrates Cobra, pflag, Viper, `cmd/root.go`, `cfg/types.go`, decode hooks, `params.yaml` flag definitions, and `convertToPosixArgs`. It is particularly important for preserving gcsfuse's historical acceptance of single-hyphen long flags, including negative numeric values that could otherwise be misread as flags.

## Risks And Test Signals
The major risk is parser regression when adding new custom types or changing flag names. Single-hyphen conversion is compatibility-sensitive and can conflict with shorthands; these tests explicitly protect `-v` and `-h`. The test signal is high for parseability, but it does not validate every semantic constraint for parsed values; that is handled by validation tests.
