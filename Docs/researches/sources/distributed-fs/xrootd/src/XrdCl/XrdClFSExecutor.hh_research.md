# sources/distributed-fs/xrootd/src/XrdCl/XrdClFSExecutor.hh

## Purpose
Declares the command dispatcher used by `xrdfs`. It provides a simple typed interface for registering command functions and executing argument vectors against one `FileSystem`.

## Important APIs, Types, And Functions
`CommandParams` is `std::vector<std::string>`. `Command` is a function pointer taking `FileSystem *`, `Env *`, and const command params, returning `XRootDStatus`. Public APIs are `FSExecutor(const URL &, Env *env = 0)`, destructor, `AddCommand`, `Execute`, and `GetEnv`.

## Control Flow
Callers construct an executor for a server URL, register commands by name, optionally mutate the env through `GetEnv`, then call `Execute` for each commandline. The first argument is expected to be the command name.

## State And Persistence
The class stores owned pointers to `FileSystem` and `Env` plus a command map. No disk persistence exists. In interactive `xrdfs`, the env is the place where current working directory and no-cwd settings survive between commands.

## Dependencies And Integration Points
Depends on `XrdClFileSystem.hh`, `XrdClEnv.hh`, `XrdClUtils.hh`, STL vector/string/map, and `URL` from included XrdCl headers. It is built directly into the `xrdfs` executable.

## Risks
The constructor contract says the executor takes ownership of `env`, so stack-allocated env arguments would cause invalid deletion. Function pointer commands limit extensibility and carry no context beyond `FileSystem` and `Env`. There is no copy/move deletion in the header, so accidental copying would duplicate owned raw pointers if attempted by future code.

## Test Signals
Compile-time tests should prevent or detect accidental copies. Runtime tests should cover ownership semantics, command registration, command lookup, and `GetEnv` mutability across multiple executions.
