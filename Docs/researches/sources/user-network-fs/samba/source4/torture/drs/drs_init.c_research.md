# sources/user-network-fs/samba/source4/torture/drs/drs_init.c Research

## Purpose
This file initializes the C-side DRSUAPI smbtorture module. It creates and registers remote RPC tests under `drs.rpc` and local/unit-style tests under `drs.unit`.

## Important APIs, Types, And Functions
`torture_drs_rpc_suite()` creates a suite, adds `torture_drs_rpc_dssync_tcase()` and `torture_drs_rpc_dsintid_tcase()`, and sets the description `DRSUAPI RPC Tests Suite`. `torture_drs_unit_suite()` creates a suite, adds `torture_drs_unit_prefixmap()` and `torture_drs_unit_schemainfo()`, and sets the description `DRSUAPI Unit Tests Suite`. `torture_drs_init()` is the smbtorture module entry point.

## Control Flow
Initialization is linear. `torture_drs_init()` builds and registers the RPC suite, then builds and registers the unit suite. Allocation failure returns `NT_STATUS_NO_MEMORY`; success returns `NT_STATUS_OK`.

## State And Persistence
The file creates in-memory `torture_suite` objects under the provided TALLOC context. It does not directly mutate directory state.

## Dependencies And Integration Points
It includes smbtorture, DRSUAPI torture declarations, SamDB headers, and `torture/drs/proto.h` for registration functions. It exposes lower-level DRS C tests to the smbtorture runner.

## Risks And Test Signals
The main signal is suite registration. Risks are small and mostly structural: missing prototypes or registration functions would remove test coverage at module initialization time.
