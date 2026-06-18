# sources/storage-engines/foundationdb/contrib/local_cluster/lib/fdb_process.py

## Purpose
`fdb_process.py` wraps `fdbserver` and `fdbcli` subprocess execution for the local-cluster helpers and provides wait loops for server readiness and database availability.

## Important APIs, Types, And Functions
`FileNotFoundError` is a local `OSError` subclass. `_ExecutablePath` resolves and validates executable paths via override or `shutil.which`; module globals `_fdbserver_path` and `_fdbcli_path` store current paths. Public setters/getters are `set_fdbserver_path`, `get_fdbserver_path`, `set_fdbcli_path`, and `get_fdbcli_path`.

`FDBServerProcess` extends `lib.process.Process` and builds `fdbserver` args for cluster file, public address, optional class, data path, and log path. It can iterate XML log files and return lines matching a severity. `FDBCLIProcess` extends `Process` and builds `fdbcli -C <cluster> --exec <commands>`. Async helpers `get_server_status`, `wait_fdbserver_up`, and `wait_fdbserver_available` poll `status json`.

## Control Flow
At import time, the module tries to discover `fdbserver` and `fdbcli`, logging warnings if absent. Running an `FDBServerProcess` constructs args and delegates to the base async process launcher. Status polling launches `fdbcli`, reads stdout with a timeout, waits for process exit, parses JSON, and retries every second until either any response is available or `client.database_status.available` is true.

## State And Persistence Behavior
Executable paths are process-global. `FDBServerProcess` causes fdbserver to persist data and XML logs under provided paths. Severity log reading opens those persisted XML files. No database state is written directly in this module beyond subprocess commands.

## Dependencies And Integration Points
It depends on `asyncio`, `glob`, `ipaddress`, `json`, `shutil`, sibling `lib.process`, and external `fdbserver`/`fdbcli` binaries. `lib.local_cluster` uses it to spawn and configure servers; `binding_test.py` uses setters to point at packaged binaries.

## Risks And Edge Cases
The custom `FileNotFoundError.filename` property returns `_strerror`, likely a bug. `get_server_status` catches builtin `TimeoutError`, not necessarily `asyncio.TimeoutError` in all contexts. It does not inspect fdbcli stderr or return code before JSON parsing. Import-time executable discovery logs warnings before top-level scripts finish configuring log handlers. `get_log_with_severity` string-matches XML lines rather than parsing XML.

## Test Signals
Tests should mock `shutil.which`, subprocess creation, fdbcli output, timeouts, JSON parse failures, severity log files, command argument construction, and executable override validation. Integration tests require real FDB binaries.
