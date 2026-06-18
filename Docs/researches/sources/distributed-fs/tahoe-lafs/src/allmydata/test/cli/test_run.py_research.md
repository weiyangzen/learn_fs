# sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_run.py

## Purpose
This module tests `allmydata.scripts.tahoe_run`: daemon startup validation, stdin-close shutdown behavior, `--allow-stdin-close`, invalid pidfile handling, and pidfile content validation.

## Important APIs, Types, and Functions
- `DaemonizeTheRealServiceTests._verify_error` builds a minimal node directory, starts `DaemonizeTheRealService` under `MemoryReactor`, runs pending `callWhenRunning` hooks, and asserts stderr and reactor stop.
- `DaemonizeStopTests` constructs daemon services with custom stdin/stdout/stderr and a `MemoryReactor` whose `stop` method records calls.
- `RunTests.test_non_numeric_pid` calls `run` directly with a fake `runApp` collector.
- `RunTests.test_pidfile_contents` uses Hypothesis text generation with `check_pid_process` and expects `InvalidPidFile` for invalid pidfile data.

## Control Flow
Startup validation writes `tahoe.cfg` and `tahoe-client.tac`, parses `run` options, starts the daemon service, manually fires reactor startup hooks, and checks for configuration errors. Stop tests start the service, fire startup hooks, simulate stdin reader connection loss with `ConnectionDone`, and check whether the reactor stop hook was called depending on flags. `run` tests bypass process execution to confirm invalid pidfile data prevents `runApp` invocation.

## State and Persistence Behavior
Tests create temporary node directories with `tahoe.cfg`, `tahoe-client.tac`, and `running.process`/pidfile data. They use in-memory streams for stdout/stderr/stdin and a `MemoryReactor` to avoid spawning real daemon processes. Hypothesis writes a local `pidfile` in the current test context.

## Dependencies and Integration Points
Dependencies include `DaemonizeTheRealService`, `RunOptions`, `run`, `parse_options`, `check_pid_process`, `InvalidPidFile`, Twisted `MemoryReactor`, `AlternateReactor`, `Failure`, `ConnectionDone`, testtools matchers, and Hypothesis. The tests sit at the boundary between CLI option parsing, Twisted service lifecycle, and pidfile safety.

## Risks and Edge Cases
Risks include accepting invalid configs, allowing port 0, privacy misconfiguration, accidental daemon survival after stdin closes, incorrectly stopping when `--allow-stdin-close` is present, proceeding with corrupt pidfiles, and parsing arbitrary pidfile content. The Hypothesis property broadens pidfile validation beyond fixed examples.

## Test Signals
The service lifecycle tests provide strong deterministic signals without real process spawning. Reactor hook manual execution is coupled to implementation details, so refactors of startup scheduling may require test updates even if behavior remains valid.
