# sources/storage-engines/foundationdb/bindings/c/test/apitester/run_c_api_tests.py

## Purpose
Python runner for API tester TOML scenarios. It creates a temporary FDB cluster per test, launches `fdb_c_api_tester`, and reports failures with client logs.

## Important APIs, types, and functions
`TestConfig` reads `[server]` TLS/process settings. `run_tester` builds the tester command, including cluster file, test file, stats, tmp dir, logging, external client library, retained library copies, and TLS paths. `run_test`, `run_tests`, and `parse_args` orchestrate execution.

## Control flow
For each selected TOML file, the script starts `TempCluster`, runs the tester with a timeout, kills on timeout, checks cluster logs, dumps client logs on failure unless disabled, and returns the failure count.

## State and persistence behavior
Creates temporary cluster data and client trace directories via `TempCluster`. It does not modify repository files.

## Dependencies and integration points
Depends on `fdb_test_runner.tmp_cluster.TempCluster`, `TLSConfig`, Python `toml`, and the built tester binary.

## Risks and test signals
CLI knob forwarding currently builds `--knob-*` style arguments, while the tester primarily consumes TOML `[[knobs]]`; this may leave CLI knobs ineffective. Signals include tester exit code, timeout reason, cluster log health, and dumped traces.
