# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/requests.c

## Purpose
`requests.c` implements small built-in ss request handlers.

## Important APIs, Types, and Functions
Public handlers are `ss_self_identify()`, `ss_subsystem_name()`, `ss_subsystem_version()`, and `ss_unimplemented()`.

## Control Flow
The first three handlers print subsystem identity data from `ss_data`. `ss_unimplemented()` reports `SS_ET_UNIMPLEMENTED` through `ss_perror()`.

## State, Persistence, Dependencies, Risks, and Test Signals
State is read-only access to subsystem name/version and generated error codes. Dependencies include `ss_internal.h` and stdio. Risks are low; handlers ignore argv and rely on a valid invocation index. Test signals are built-in commands printing expected name/version and unimplemented commands reporting the generated error.
