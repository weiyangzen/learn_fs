# sources/user-network-fs/samba/source4/lib/registry/registry.h

## Purpose

`registry.h` is the central private/public contract for Samba source4 registry code. It defines both the low-level hive API for one backing store and the higher-level registry API that mounts predefined-key views over one or more hives.

## Important APIs, Types, and Functions

The hive layer centers on `struct hive_key` and `struct hive_operations`, whose methods enumerate, open, add, delete, flush, get/set values, delete values, get/set security descriptors, and query key metadata. The registry layer centers on `struct registry_context`, `struct registry_key`, `struct registry_value`, and `struct registry_operations`, with similar operations plus predefined-key resolution, load/unload, notifications, and hive mounting. The header declares REGF, LDB, directory, Samba-local, remote RPC, and Wine open functions; utility conversion helpers; absolute-path helpers; diff callbacks; and diff load/save/apply entry points.

## Control Flow

Callers open a hive through `reg_open_hive()` or a concrete backend, or open a whole registry through `reg_open_local()`, `reg_open_samba()`, or `reg_open_remote()`. Generic wrappers dispatch through the operation tables. Mounting imports a hive root under a predefined handle and optional path elements. Diff generation compares two registry contexts and emits callback events; diff loading parses a patch file and invokes callbacks that apply changes or save another patch format.

## State and Persistence Behavior

The header does not persist state itself but defines the ownership and mutation boundaries. Hive implementations own backing storage and flush semantics. Registry contexts own mounted predefined keys. `DATA_BLOB` values carry caller-managed talloc memory. Security descriptors and notifications are optional backend features and may return `WERR_NOT_SUPPORTED`.

## Dependencies and Integration Points

This file includes talloc, WERROR, NTSTATUS, security descriptors, time, and data blobs. It is included by REGF, LDB, local, RPC, patchfile, Python binding, tools, and tests. It bridges generated winreg constants and Samba-specific backend implementations.

## Risks and Edge Cases

Operation-table APIs rely on every backend honoring optional output pointer conventions and consistent error codes. Several TODO-style areas are exposed in the contract, including notifications, load/unload support, and security descriptor support. The `access_mask` argument to `reg_key_add_abs()` exists but not all backends use it. Callers must understand that hive keys and registry keys are distinct wrappers even when a local mounted hive makes them look similar.

## Test Signals

`tests/hive.c`, `tests/registry.c`, and `tests/diff.c` exercise the declared surface through LDB, REGF, local registry, and diff paths. Compile coverage across Python bindings and tools catches signature drift. Useful additional tests would verify unsupported-operation behavior for every backend method.

Source-read signal: reviewed complete local file (531 lines).
