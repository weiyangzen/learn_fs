# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_exclave_fs_helper.cpp

## Scope

This C++ helper implements APFS volume-group lookup for the exclave filesystem bridge using IOKit service matching.

## Public And Internal APIs Covered

- Defines `vfs_exclave_fs_query_volume_group(const uuid_string_t, bool *)`.

## Control Flow And Behavior

On macOS targets, the function validates the input UUID string, creates an `AppleAPFSVolume` service matching dictionary, filters by `VolGroupUUID`, and sets `*exists` if a matching service is found. It releases all IOKit objects on exit.

On non-macOS targets, it returns `ENOTSUP`.

## State And Data Structures

No persistent state is kept. Temporary `OSDictionary`, `OSString`, and `IOService` references are allocated and released in one call.

## Dependencies

Depends on IOKit `IOService` matching, `IOPlatformExpert`, UUID parsing, and the C exclave FS header.

## Risks And Invariants

- The caller-visible result is initialized to false only on macOS builds; non-macOS returns `ENOTSUP`.
- All IOKit references must be released on every error path.
- `OSString::withCStringNoCopy()` relies on the input string remaining valid for the match setup.
