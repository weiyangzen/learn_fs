# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/CMakeLists.txt

## Purpose

This CMake file selects stackable FSAL subdirectories. It conditionally includes FSAL_NULL and always includes FSAL_MDCACHE. The source was read as a complete 25-line file.

## Important APIs, Types, and Functions

The relevant CMake commands are `if(USE_FSAL_NULL)`, `add_subdirectory(FSAL_NULL)`, `endif`, and `add_subdirectory(FSAL_MDCACHE)`.

## Control Flow

During configuration, CMake adds the NULL stackable FSAL only when enabled, then adds MDCACHE unconditionally so the metadata cache object library is built.

## State and Persistence Behavior

No runtime state exists here. It controls generated build graph state.

## Dependencies and Integration Points

It is the parent build entry for stackable FSAL implementations under `src/FSAL/Stackable_FSALs`, integrating MDCACHE into the wider NFS-Ganesha build.

## Risks and Edge Cases

Making MDCACHE unconditional means missing dependencies in FSAL_MDCACHE break stackable FSAL builds. Conditional flags must stay aligned with top-level build options.

## Test Signals

Configure builds with `USE_FSAL_NULL` on/off and verify `FSAL_MDCACHE` is always entered and produces the expected object target.
