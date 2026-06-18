# sources/storage-engines/foundationdb/fdbserver/kvstore/FDBExecHelper.cpp

## Purpose
`FDBExecHelper.cpp` provides helper-process execution support for storage snapshot workflows and stores per-storage-engine version information for trace output. It invokes an external snapshot command outside simulation and uses deterministic copy-based behavior in simulation.

## Important APIs, Types, and Functions
`ExecCmdValueString` parses a command string into binary path and space-delimited arguments. `spawnProcess(...)` executes a binary and returns an integer status. On unsupported platforms it is a success stub; on supported POSIX platforms `fork_child(...)` creates a pipe, forks, redirects stdout/stderr, and calls `execv`. `setupTraceWithOutput(...)` attaches bounded child output to trace events. `execHelper(...)` builds snapshot command arguments. `setDataVersion`, `setDataDurableVersion`, and `printStorageVersionInfo` maintain process-local storage UID version data.

## Control Flow
For non-simulated execution, `execHelperImpl` appends FoundationDB-managed arguments such as `--path`, optional `--tlog-spill-path`, `--version`, `--role`, and `--uid`, then awaits `spawnProcess`. In simulation it creates a snapshot directory with `/bin/mkdir` and copies the source folder with `/bin/cp -a`. `spawnProcess` optionally delays async calls in simulation, forks the child, sets the pipe read end nonblocking, loops with `waitpid(..., WNOHANG)`, drains output up to `SERVER_KNOBS->MAX_FORKED_PROCESS_OUTPUT`, handles timeout, and traces failures or success.

## State and Persistence Behavior
This file does not persist data directly. Its side effects are external process execution and, in simulation, filesystem directory creation/copying for snapshots. The global `workerStorageVersionInfo` map is process-local state keyed by network address and storage UID. Child output is bounded before entering trace fields.

## Dependencies and Integration Points
The implementation depends on Flow futures, tracing, network/simulator globals, `FDB_VT_VERSION`, server knobs, Boost headers where available, and POSIX process APIs. It integrates with storage snapshot callers through `FDBExecHelper.h` and simulator lifecycle through `destroyChildProcess`.

## Risks
Command parsing splits only on spaces and does not implement shell quoting. Timeout handling returns `-1` but does not explicitly kill a long-running child in the shown parent loop. The function writes child output to stdout as well as trace setup, which may be noisy.

## Test Signals
There is no local `TEST_CASE`. Signals are simulator branches, trace events such as `SpawnProcessFailure`, `SpawnProcessCommandStatus`, and `SnapDelaySpawnProcess`, plus storage version trace output.
