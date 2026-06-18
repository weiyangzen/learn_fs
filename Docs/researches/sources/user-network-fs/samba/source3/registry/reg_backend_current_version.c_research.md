# sources/user-network-fs/samba/source3/registry/reg_backend_current_version.c

## Purpose

`reg_backend_current_version.c` implements a virtual registry overlay for `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion`, dynamically exposing Samba-compatible Windows version values while delegating subkeys and unrelated value fetches to the default registry DB backend.

## Important APIs, Types, and Functions

- `current_version_fetch_values()` normalizes the key path and returns virtual `SystemRoot` and `CurrentVersion` values for the target key.
- `current_version_fetch_subkeys()` delegates to `regdb_ops.fetch_subkeys`.
- `current_version_reg_ops` exposes the overlay operations table.

## Control Flow

When values are fetched, the key is duplicated and normalized. If the path does not match the normalized CurrentVersion prefix condition, the request is delegated to `regdb_ops.fetch_values()`. For the CurrentVersion key, it adds `SystemRoot = c:\Windows` and `CurrentVersion = <SAMBA_MAJOR_NBT_ANNOUNCE_VERSION>.<SAMBA_MINOR_NBT_ANNOUNCE_VERSION>` to the provided container and returns the value count.

## State and Persistence

No persistent state is written. Values are generated dynamically. Subkeys are still read from the default registry backend.

## Dependencies and Integration Points

It depends on registry value containers, path normalization, Samba version macros, and the default `regdb_ops`. Hook registration elsewhere maps the CurrentVersion path to `current_version_reg_ops`.

## Risks and Edge Cases

The string comparison uses `strncmp(path, KEY_CURRENT_VERSION_NORM, strlen(path))`, so prefix behavior is sensitive to normalized path length and should be tested for parent/child paths. The overlay does not merge default DB values for the matched key; it returns only virtual values it adds.

## Test Signals

Tests should fetch exact CurrentVersion values, fetch subkeys through delegation, query unrelated paths through delegation, and verify normalized case/backslash behavior.
