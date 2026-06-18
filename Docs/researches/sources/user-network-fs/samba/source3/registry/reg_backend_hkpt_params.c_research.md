# sources/user-network-fs/samba/source3/registry/reg_backend_hkpt_params.c

## Purpose

`reg_backend_hkpt_params.c` implements a dynamic registry backend for HKPT performance counter parameters. It exposes generated counter names and help text under value names expected by this hive.

## Important APIs, Types, and Functions

- `hkpt_params_fetch_values()` adds `Counters` and `Help` `REG_MULTI_SZ` values from performance counter helpers.
- `hkpt_params_fetch_subkeys()` delegates subkey fetching to `regdb_ops`.
- `hkpt_params_reg_ops` publishes the backend operation table.

## Control Flow

Fetching values obtains the performance counter base index, asks for counter names and help buffers, adds each buffer as a registry multi-string value, frees non-empty buffers, and returns the value count. Subkey requests use the default DB backend.

## State and Persistence

No values are persisted by this backend; all values are generated dynamically from performance counter data. Subkeys remain persisted by `regdb_ops`.

## Dependencies and Integration Points

It depends on `reg_perfcount_get_base_index()`, `reg_perfcount_get_counter_names()`, `reg_perfcount_get_counter_help()`, registry value containers, and default `regdb_ops`. Hook registration maps HKPT parameter paths to this ops table.

## Risks and Edge Cases

- Buffer ownership depends on performance counter helpers returning heap buffers only when size is positive.
- The file intentionally uses `Counters` rather than `Counter`, matching HKPT expectations.
- No store operations are supplied, so mutation should fall back or fail according to dispatcher semantics.

## Test Signals

Tests should verify generated `Counters` and `Help` values, zero-size buffer handling, delegation of subkeys, and correct behavior when performance counter helpers fail or return empty data.
