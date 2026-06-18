# sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli_node_api.py

## Purpose
This helper module exposes a small API for starting, observing, and stopping a Tahoe node via the CLI runner in tests. It also provides protocols for waiting for expected process output and adapting child process file descriptors to Twisted protocols.

## Important APIs, Types, and Functions
- Public `__all__`: `CLINodeAPI`, `Expect`, `on_stdout`, `on_stdout_and_stderr`, and `on_different`.
- `Expect` is a `Protocol` that buffers output and returns Deferreds that fire once expected bytes appear.
- `_ProcessProtocolAdapter` maps child stdout/stderr file descriptors to protocols and forwards connection/data/lost events.
- `on_stdout`, `on_stdout_and_stderr`, and `on_different` are convenience constructors for common fd mappings.
- `CLINodeAPI` is an `attr.s` class with `reactor`, `basedir`, and optional `process`.
- `CLINodeAPI._execute` spawns `python -b -m allmydata.scripts.runner ...`.
- `run`, `stop`, `stop_and_wait`, `active`, and `cleanup` manage process lifecycle.

## Control Flow
Tests create a `CLINodeAPI` with a reactor and node `FilePath`, then call `run` with a process protocol. `run` validates that the protocol provides `IProcessProtocol`, constructs runner arguments, spawns the process, and touches the exit-trigger file via `active`. Output protocols can use `Expect.expect` to wait until specific bytes arrive. `stop_and_wait` repeatedly sends `TERM` until Twisted reports `ProcessExitedAlready`, yielding via `deferLater` between attempts. `cleanup` wraps stopping and tolerates `ProcessTerminated`.

## State and Persistence Behavior
The helper exposes path properties for `running.process`, `node.url`, `private/storage.furl`, `private/introducer.furl`, `tahoe.cfg`, and the client exit-trigger file. `active` touches the exit-trigger file so the launched client should terminate after its built-in timeout if tests fail to stop it. Process state is stored in `self.process`.

## Dependencies and Integration Points
Dependencies include Twisted `Protocol`, `ProcessProtocol`, `IProcessProtocol`, `Deferred`, `deferLater`, `FilePath`, process errors, Eliot logging decorators, and Tahoe `_Client.EXIT_TRIGGER_FILE`. The module integrates tests with the actual `allmydata.scripts.runner` module by spawning a Python subprocess.

## Risks and Edge Cases
Risks include unhandled child fd output, expectations that never fire if output differs, process cleanup loops, process already exited conditions, ENOENT when checking activity before files exist, and environment leakage because subprocesses inherit `os.environ`. The output adapter intentionally logs unhandled fd data instead of failing directly.

## Test Signals
This is test infrastructure rather than a test suite. It enables higher-level CLI node integration tests to observe stdout/stderr and manage node lifetime. Its own reliability depends on Twisted process behavior and the exit-trigger safety file.
