# sources/storage-engines/foundationdb/fdbcli/tests/fdbcli_tests.py

## Purpose

`fdbcli_tests.py` is an integration test driver for fdbcli. It runs a built `fdbcli` binary against a real test cluster, invokes commands with `--exec` or interactive stdin, and asserts exact output or observable cluster state through status JSON.

## Important APIs, Types, and Functions

- `run_fdbcli_command` and `run_fdbcli_command_and_get_error` wrap `subprocess.run` for stdout/stderr assertions.
- `enable_logging` decorates test functions with per-test logging.
- Command tests include `maintenance`, `setclass`, `lockAndUnlock`, `kill`, `killall`, `suspend`, `versionepoch`, `consistencycheck`, `datadistribution`, `transaction`, `clearrange_prefix`, `coordinators`, `exclude`, `throttle`, `profile`, `triggerddteaminfolog`, `idempotency_ids`, `integer_options`, and `tls_address_suffix`.
- `get_value_from_status_json`, `read_system_key`, `get_fdb_process_addresses`, and `wait_for_database_fully_recovered` are shared helpers.
- The `__main__` block parses build directory, cluster file, process count, and optional external client library.

## Control Flow

The script builds a command template `[build_dir/bin/fdbcli, -C, cluster_file, --exec]`, verifies database availability, then runs a set of tests. Single-process clusters run most command tests; multi-process clusters run coordinator, exclude, and kill-all tests. Several unstable or disruptive tests are intentionally disabled with comments. Some workflows use interactive `Popen` without `--exec` to preserve state across commands or respond to prompts.

## State and Persistence Behavior

The tests mutate the cluster: they lock/unlock, kill or suspend processes, toggle maintenance, data distribution, consistency check, version epoch, transaction keys, coordinator configuration, process exclusion, profiling config, and idempotency ID metadata. Cleanup is embedded in individual tests where practical, and recovery waits are used after disruptive operations.

## Dependencies and Integration Points

The script depends on Python standard libraries, a running FoundationDB cluster, the built fdbcli binary, status JSON schema, and exact CLI output strings. External client testing is supported by setting `FDB_NETWORK_OPTION_DISABLE_LOCAL_CLIENT` and `FDB_NETWORK_OPTION_EXTERNAL_CLIENT_LIBRARY`.

## Risks and Edge Cases

The suite is output-fragile: harmless wording changes break assertions. Many tests assume local `127.0.0.1` addresses and specific process counts. Some actions are disruptive and can race recovery; the script uses sleeps and polling but can still be environment-sensitive. The `enable_logging` decorator adds a new handler on every invocation, which can duplicate logs if tests are rerun in-process.

## Test Signals

The file itself is the test signal for fdbcli behavior. In this subset it directly covers `versionepoch`, `triggerddteaminfolog`, shared transaction parsing/dispatch, status JSON, TLS validation, and much of `fdbcli.cpp`. The throttle test exists but is not active in the default single-process path.
