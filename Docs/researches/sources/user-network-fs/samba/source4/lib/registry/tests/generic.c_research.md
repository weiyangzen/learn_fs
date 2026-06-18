# sources/user-network-fs/samba/source4/lib/registry/tests/generic.c

## Purpose

`tests/generic.c` is the top-level registry torture suite and focused unit coverage for registry value formatting helpers.

## Important APIs, Types, and Functions

It defines tests for `str_regtype()`, `reg_val_data_string()` across DWORD, DWORD_BIG_ENDIAN, QWORD, SZ, binary, and empty data, and `reg_val_description()` with normal and NULL names. `torture_registry()` assembles the generic tests plus the hive, registry, and diff sub-suites.

## Control Flow

Each simple test constructs minimal `DATA_BLOB` inputs, calls the formatting helper, and compares exact strings. The suite then nests `torture_registry_hive()`, `torture_registry_registry()`, and `torture_registry_diff()` so one registry test entry covers utility functions and backend behavior.

## State and Persistence Behavior

The file itself has no persistent state. It uses the torture context for allocations and passes transient blobs to conversion helpers. Nested suites create their own temp hives and registries.

## Dependencies and Integration Points

It depends on `registry.h`, winreg constants, loadparm/torture infrastructure, and generated test prototypes. It validates helper behavior consumed by `regtree`, `regshell`, Python `str_regtype()`, and diff/patch output paths.

## Risks and Edge Cases

The SZ tests convert without a trailing NUL in one case and manually shorten the blob to assert truncation behavior, but REG_MULTI_SZ and unsupported types are not covered. DWORD_BIG_ENDIAN currently expects the same little-endian formatting as DWORD, which documents existing behavior but may not match intuitive big-endian display semantics.

## Test Signals

Exact string comparisons catch accidental display format changes. Additional tests should cover `reg_string_to_val()` parsing, `REG_EXPAND_SZ`, `REG_MULTI_SZ`, invalid data lengths that trigger assertions, and round-trip display/parse behavior.

Source-read signal: reviewed complete local file (179 lines).
