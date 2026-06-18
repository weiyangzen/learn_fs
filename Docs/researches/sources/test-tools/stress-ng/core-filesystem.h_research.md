# sources/test-tools/stress-ng/core-filesystem.h

## Purpose

This header declares the filesystem utility contract used by stress-ng core code and stressors. It also defines cache-drop flag constants used to request Linux page-cache, slab-object, or combined cache dropping.

## Important APIs, Types, And Functions

The header exposes temp-path APIs, filename and temp-directory construction, filesystem sizing and inode queries, robust file read/write wrappers, file descriptor and pipe helpers, directory entry utilities, filesystem type reporting, fd closing, write-lifetime hints, chattr cleanup, recursive temp cleanup, and cache dropping. `STRESS_DROP_CACHE_PAGE_CACHE`, `STRESS_DROP_CACHE_SLAB_OBJECTS`, and `STRESS_DROP_CACHE_ALL` define the accepted `stress_fs_drop_caches` mask.

## Control Flow

Consumers include this header to call filesystem helpers without knowing platform-specific implementation details. Return types consistently report byte counts, boolean predicates, or negative errno-style failures depending on the helper. The APIs are intentionally low-level and leave policy decisions, such as whether a failure is fatal, to the caller.

## State And Persistence Behavior

The declarations cover helpers that read and mutate filesystem state, including temporary directory creation/removal and global Linux cache dropping. The header itself owns no state, but callers must account for implementation-side static caches and non-reentrant static return buffers in filesystem type reporting.

## Dependencies And Integration Points

The header includes `stress-ng.h`, so it depends on project-wide types such as `stress_args_t`, `stress_type_id_t`, and shim-visible platform types. It is consumed by memory, CPU ignition, process diagnostics, stressor implementations, and option parsing.

## Risks And Test Signals

The contract is broad and used throughout stress-ng, so signature changes are high blast radius. Tests should compile on Linux and non-Linux targets, verify drop-cache flags are constrained to declared values, and validate callers handle negative returns from Linux-specific operations.
