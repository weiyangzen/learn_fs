<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/branches.cpp -->
# sources/user-network-fs/mergerfs/src/branches.cpp

## Purpose

This file implements the thread-safe mutable branch list used by mergerfs. It parses branch expressions, expands globs, canonicalizes paths, preserves per-branch modes/min-free-space, applies add/remove/set operations atomically with shared/unique locks, and detects read-only backing filesystems. The source was read as a complete 564-line file (11604 bytes).

## Important APIs, Types, and Functions

functions: `Branches::Impl::Impl`, `Branches::Impl::minfreespace`, `Branches::Impl::from_string`, `Branches::Impl::to_string`, `Branches::Impl::to_paths`, `Branches::from_string`, `Branches::to_string`, `Branches::find_and_set_mode_ro`, `SrcMounts::SrcMounts`, `SrcMounts::from_string`, `SrcMounts::to_string`, `split`, `parse_mode`, `parse_minfreespace`, and 13 more

## Control Flow

Branch updates clone the current shared implementation, parse the requested operation, mutate the clone, then swap it under a unique lock only if no concurrent writer changed the shared pointer. Readers take shared locks and format or project the current branch vector.

## State and Persistence Behavior

Branch state is copy-on-write through a `shared_ptr` to `Branches::Impl`; each `Branch` stores path, mode, and either explicit min-free-space or a pointer to the collection default. No file-backed persistence is performed here.

## Dependencies and Integration Points

direct includes: `branches.hpp`, `ef.hpp`, `errno.hpp`, `from_string.hpp`, `fs_glob.hpp`, `fs_is_rofs.hpp`, `fs_realpathize.hpp`, `base_types.h`, `num.hpp`, `str.hpp`, `syslog.hpp`, `mutex`, `optional`, `shared_mutex`, and 2 more

## Risks and Edge Cases

Branch parsing is user-facing and concurrency-sensitive. Errors in copy-on-write pointer relinking, glob expansion, min-free-space parsing, or atomic swap retries can expose stale paths, skip valid branches, or race runtime updates.

## Test Signals

Branch expression tests for set/add/remove operations, glob and missing-path behavior, mode/min-free-space parsing, concurrent writer retry behavior, and read-only filesystem detection with mounted fixtures.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/branches.cpp -->
