# sources/user-network-fs/samba/source3/registry/reg_api_util.c

## Purpose

`reg_api_util.c` provides a convenience wrapper for opening a complete registry path that includes the hive prefix.

## Important APIs, Types, and Functions

- `reg_open_path()` parses `orig_path`, opens the hive, and optionally opens the remaining subkey path with requested access.

## Control Flow

The function duplicates the input path, finds the first backslash, and treats paths without a non-empty suffix as hive-only opens. For subkey paths it terminates the hive component, opens the hive with `KEY_ENUMERATE_SUB_KEYS`, opens the remainder with the caller’s desired access, frees the temporary hive key, and returns the final key.

## State and Persistence

No state is owned here. It allocates temporary path memory with `SMB_STRDUP()` and registry key objects through `reg_openhive()`/`reg_openkey()`.

## Dependencies and Integration Points

It depends on `reg_api.h`, registry types, security tokens, and registry path utilities. It is a helper for callers that receive full strings such as `HKLM\Software\...`.

## Risks and Edge Cases

- It mutates the duplicated string in place and must free it on all paths.
- Hive-only detection treats a trailing backslash with no key behind it as opening the hive.
- Intermediate hive access is always enumerate-subkeys, which must be enough for the final open traversal.

## Test Signals

Tests should cover hive-only paths, trailing backslash paths, full key paths, unknown hive errors, allocation failure handling where injectable, and access-denied propagation from final open.
