# sources/storage-engines/foundationdb/contrib/local_cluster/lib/process.py

## Purpose
`process.py` is a small asyncio subprocess wrapper used by local-cluster and binding-test utilities.

## Important APIs, Types, And Functions
`Process(executable, arguments=None, env=None)` stores command metadata and an optional environment. `run()` launches `asyncio.subprocess.create_subprocess_exec` with stdin/stdout/stderr pipes and returns the underlying process. Properties/methods `pid`, `kill`, `terminate`, `return_code`, and `is_running` expose process status and control.

## Control Flow
Callers construct a `Process`, await `run`, then interact with the returned `asyncio.subprocess.Process` or wrapper methods. `kill` and `terminate` raise if called before `run`.

## State And Persistence Behavior
State is the executable, args, env, and the process handle. Persistence and side effects are determined by the child process, not this wrapper.

## Dependencies And Integration Points
It depends on `asyncio`, `logging`, and typing helpers. `FDBServerProcess`, `FDBCLIProcess`, and `binding_test.TestSet` use it as their process-launch primitive.

## Risks And Edge Cases
The wrapper does not wait after kill/terminate, does not drain pipes automatically, and can deadlock callers that wait on processes producing large output without reading. `is_running` returns true if a pid exists and return code is `None`, but the return code may not update until waited/polled by asyncio. It logs command arguments, which may reveal sensitive values.

## Test Signals
Tests should launch short-lived commands, verify stdout/stderr pipes, pid/return code transitions, custom environment propagation, and pre-run kill/terminate errors.
