# sources/user-network-fs/mergerfs/src/procfs.hpp

## Purpose
Declares the procfs support API used to cache proc directory descriptors and read thread names.

## Important APIs, Types, and Functions
Exports `procfs::PROC_SELF_FD_FD`, `init()`, `shutdown()`, and `get_name(int tid)`.

## Control Flow
The header only declares functions; callers must invoke `init()` before helpers that rely on cached descriptors and `shutdown()` during teardown.

## State and Persistence Behavior
State is the externally defined proc fd. The API does not persist data.

## Dependencies and Integration Points
Includes `<string>` and integrates with low-level fd and thread diagnostics.

## Risks and Edge Cases
Consumers must respect initialization order. `PROC_SELF_FD_FD` is mutable global state and can become invalid after shutdown.

## Test Signals
Compile users against the declarations and run lifecycle tests covering init, read, shutdown, and repeated init.
