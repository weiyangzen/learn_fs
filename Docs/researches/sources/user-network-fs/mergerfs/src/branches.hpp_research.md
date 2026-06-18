<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/branches.hpp -->
# sources/user-network-fs/mergerfs/src/branches.hpp

## Purpose

This header declares the thread-safe mergerfs branch collection, its internal vector-backed implementation, and `SrcMounts` read-only projection used by the config interface. The source was read as a complete 113-line file (2519 bytes).

## Important APIs, Types, and Functions

types: `Branches`, `Impl`, `SrcMounts` functions: `from_string`, `to_string`, `to_paths`, `find_and_set_mode_ro` macros: `MINFREESPACE_DEFAULT`

## Control Flow

Branch updates clone the current shared implementation, parse the requested operation, mutate the clone, then swap it under a unique lock only if no concurrent writer changed the shared pointer. Readers take shared locks and format or project the current branch vector.

## State and Persistence Behavior

Branch state is copy-on-write through a `shared_ptr` to `Branches::Impl`; each `Branch` stores path, mode, and either explicit min-free-space or a pointer to the collection default. No file-backed persistence is performed here.

## Dependencies and Integration Points

direct includes: `branch.hpp`, `fs_path.hpp`, `strvec.hpp`, `tofrom_string.hpp`, `cstdint`, `memory`, `shared_mutex`, `string`, `vector`

## Risks and Edge Cases

Branch parsing is user-facing and concurrency-sensitive. Errors in copy-on-write pointer relinking, glob expansion, min-free-space parsing, or atomic swap retries can expose stale paths, skip valid branches, or race runtime updates.

## Test Signals

Branch expression tests for set/add/remove operations, glob and missing-path behavior, mode/min-free-space parsing, concurrent writer retry behavior, and read-only filesystem detection with mounted fixtures.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/branches.hpp -->
