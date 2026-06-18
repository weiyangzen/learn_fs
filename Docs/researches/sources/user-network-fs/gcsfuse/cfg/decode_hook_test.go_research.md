## sources/user-network-fs/gcsfuse/cfg/decode_hook_test.go

Purpose: Tests Viper decode behavior for primitive, slice, duration, path, and custom config types.

Important APIs/types/functions: helper `bindFlag`; `TestParsingSuccess` defines a local config with `Octal`, bool, string, int, float, duration, string/int slices, `LogSeverity`, `Protocol`, and `ResolvedPath`; `TestParsingError` checks invalid `Octal`, `LogSeverity`, `Protocol`, and `DirectPathStrategy`.

Control flow: each case creates a pflag set, binds it to Viper, parses test args, unmarshals with `viper.DecodeHook(DecodeHook())`, then asserts parsed values or error messages. Path tests cover `~`, absolute paths, and relative paths resolved against `gcsfuse-parent-process-dir`.

State and persistence: temporarily sets and cleans `gcsfuse-parent-process-dir` in one case; otherwise stateless. Tests run subcases in parallel.

Dependencies and integration points: exercises `DecodeHook` plus custom text unmarshalling in `types.go` and environment-dependent path resolution.

Risks: parallel environment mutation can be fragile because the env var is process-global; current setup confines mutation to one subtest but parallel scheduling remains a consideration. Error assertion for invalid octal only checks non-nil when no expected string is specified.

Test signals: strong signal that CLI/config parsing builds typed config values as expected.
