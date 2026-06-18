# sources/distributed-fs/xrootd/src/XrdCl/XrdClFSExecutor.cc

## Purpose
Implements `FSExecutor`, the small dispatcher used by `xrdfs` to bind textual command names to functions operating on a shared `FileSystem` and environment.

## Important APIs, Types, And Functions
Implements the constructor, destructor, `AddCommand`, and `Execute`. The constructor creates a `FileSystem` for the target URL, uses the supplied `Env` or allocates a new one, and stores `ServerURL`. `AddCommand` inserts into the command map. `Execute` logs the commandline and dispatches by the first argument.

## Control Flow
An executor is constructed by `CreateExecutor` in `XrdClFS.cc`, then commands are registered. On execution, the argument vector is copied into a printable string for debug logs, empty commands return shell status `1`, each parameter is dump-logged, the first argument is looked up in `pCommands`, and the corresponding function pointer is invoked with `pFS`, `pEnv`, and the original args.

## State And Persistence
The executor owns `pFS` and `pEnv` and deletes both in the destructor. Command registration state is an in-memory `std::map<std::string, Command>`. The environment persists command-session values such as current directory across interactive commands.

## Dependencies And Integration Points
Depends on `FileSystem`, `Env`, `Log`, `DefaultEnv`, status constants, and STL iterators. It is linked into the `xrdfs` executable and is not a general shell framework beyond this tool.

## Risks
Ownership is raw-pointer based; constructor allocation failures or future partial-construction changes would need care. `Execute` returns integer `1` for empty args via implicit `XRootDStatus` construction rather than a named error. Duplicate registration logs and fails but leaves the original command. There is no synchronization around command registration or execution.

## Test Signals
Tests should verify constructor env ownership, `ServerURL` insertion, duplicate command rejection, unknown command status, empty command handling, dispatch argument preservation, and destructor cleanup under leak sanitizers.
