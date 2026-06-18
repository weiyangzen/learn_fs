# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_runner.py

## Purpose
This Twisted Trial test module exercises Tahoe-LAFS command-line runner behavior around parsing, `bin/tahoe` subprocess execution, node creation, node runtime lifecycle, stdin-close handling, and pid-file locking. It is not an implementation module, but it is a high-value integration test for user-visible CLI contracts and process management.

## Important APIs, Types, And Functions
`get_root_from_file(src)` derives a project root from an installed module path, handling `site-packages` and source-layout cases. `run_bintahoe(extra_argv, python_options=None)` is the central subprocess helper: it runs `python -b -m allmydata.scripts.runner`, encodes argv through `unicode_to_argv`, captures stdout and stderr, decodes using the preferred locale, and returns `(out, err, returncode)`.

`ParseOrExitTests` validates non-ASCII parse errors through `run_cli_unicode`. `BinTahoe` validates direct runner invocation, Python interpreter option forwarding, and Eliot destination option parsing. `CreateNode` calls CLI creation commands via `run_cli` and `parse_cli` to verify node, client, and introducer directory creation. `RunNode` uses `CLINodeAPI`, `Expect`, and process stdout matching to exercise `tahoe run` for introducers and clients. `OnStdinCloseTests` targets `allmydata.scripts.tahoe_run.on_stdin_close` using `MemoryReactorClock`. `PidFileLocking` tests `allmydata.util.pid.check_pid_process`, `_pidfile_to_lockpath`, and `ProcessInTheWay`.

## Control Flow
The file mixes synchronous testtools matchers, `inlineCallbacks`, and Tahoe's Eliot-aware `inline_callbacks`. CLI creation tests build several command variants for each node kind: explicit `--basedir`, positional basedir, global `--node-directory`, unquiet output, duplicate-directory rejection, and usage-error paths. Runtime tests create nodes with `run_bintahoe`, mutate generated config when needed, spawn `tahoe run`, wait for startup text, poll for readiness files, stop the process, and restart to assert stable FURLs.

Bad-directory tests intentionally race two expected outputs: an error message and a possible normal startup line. A `DeferredList(..., fireOnOneCallback=True)` asserts the error arrives first and then waits for process completion to avoid dirty reactor state. Stdin-close tests simulate platform-specific reader shutdown: normal reactor readers on POSIX and explicit `writeConnectionLost`/`readConnectionLost` on Windows.

## State And Persistence Behavior
The tests create real filesystem node directories under `test_runner/...`. They assert persistent artifacts such as `tahoe.cfg`, `tahoe-client.tac`, `tahoe-introducer.tac`, `introducer.furl`, `storage.furl`, `twistd.pid`, and `node.url`. Important persistence contracts include storage being enabled for `create-node`, disabled for `create-client`, reserved space being written for storage nodes, stable introducer and storage FURLs across restarts, and pid-file removal after graceful POSIX shutdown.

`PidFileLocking` writes a small helper script and uses a child process to hold the lock corresponding to a pid file. This deliberately tests interprocess state rather than only same-process locking, because the lock library allows reentrant locking inside one process.

## Dependencies And Integration Points
The module depends on Twisted reactor/process APIs, `twisted.python.usage`, platform detection, `FilePath`, Tahoe CLI helpers (`run_cli`, `parse_cli`, `CLINodeAPI`), encoding utilities, file utilities, pid-file utilities, and Eliot logging. It also depends on real child-process invocation of the installed/source runner, so it verifies packaging and module-entry behavior beyond unit-level parser calls.

## Risks And Edge Cases
These tests are sensitive to platform behavior, especially Windows process termination and stdin simulation. They also rely on stdout text such as `client running` and `introducer running`, so changes in log wording can break tests without changing core behavior. Locale decoding in `run_bintahoe` can surface environment-dependent failures. Runtime tests may be slower and more fragile than pure unit tests because they spawn real processes and poll filesystem readiness.

## Test Signals
Passing tests indicate that non-ASCII CLI errors are preserved, global runner options are parsed correctly, Eliot destination validation rejects malformed inputs, node creation creates correct files and rejects invalid forms, `tahoe run` starts usable nodes and preserves FURLs across restarts, stdin close callbacks run and swallow callback exceptions, and pid-file locking detects another live process holding the lock.
