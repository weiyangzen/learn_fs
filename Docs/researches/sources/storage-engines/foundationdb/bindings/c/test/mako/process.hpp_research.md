# sources/storage-engines/foundationdb/bindings/c/test/mako/process.hpp

## Purpose
`process.hpp` defines the process role enum used by Mako logging and process branching.

## Important APIs, Types, and Functions
- `enum class ProcKind { MAIN, WORKER, STATS, ADMIN }` names the process categories used by the benchmark and admin server components.

## Control Flow
`mako.cpp` initializes `ProcKind::MAIN`, changes children to `WORKER` or `STATS` after fork, and uses the role to choose the worker or stats entry point. Other headers use distinct tag types for logger construction, while this enum represents high-level process identity.

## State and Persistence Behavior
The file has no state or persistence behavior. Runtime state is a simple enum value in each process.

## Dependencies and Integration Points
It is intentionally dependency-free. Its values integrate with process orchestration in `mako.cpp` and conceptually with `admin_server`/logging.

## Risks
The enum is small but central enough that adding a role requires checking every process switch and logger mapping. There is no default behavior encoded here.

## Test Signals
Build coverage and Mako process smoke tests are sufficient. Any new process role should be accompanied by a fork-path or admin-path test.
