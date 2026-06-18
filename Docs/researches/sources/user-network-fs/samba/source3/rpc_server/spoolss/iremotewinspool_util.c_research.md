# Research: sources/user-network-fs/samba/source3/rpc_server/spoolss/iremotewinspool_util.c

## Purpose

`iremotewinspool_util.c` provides a compact translation table from MS-RPRN `IRemoteWinspool` async opcodes to Samba's existing `spoolss` NDR opcodes. It lets the server proxy or dispatch supported async winspool calls through the corresponding synchronous or extended spoolss operation identifiers.

## Important APIs, Types, and Functions

- `_PAR_MAPPING(NAME)`: maps `NDR_WINSPOOL_ASYNC##NAME` to `NDR_SPOOLSS_##NAME`.
- `_PAR_MAPPING_EX(NAME)`: maps to an `EX` spoolss opcode, used where the async API corresponds to an extended spoolss call such as `OPENPRINTEREX`.
- `_PAR_MAPPING_2(NAME)`: maps to a `2` spoolss opcode, used for `GETPRINTERDRIVER2`.
- `proxy_table[]`: static opcode mapping table grouped by protocol sections: printer management, driver management, port management, processor management, monitor management, form management, job management, job printing, named job properties, and branch-office logging.
- `iremotewinspool_map_opcode(uint16_t opcode, uint16_t *proxy_opcode)`: linear lookup that writes the mapped spoolss opcode and returns `true`, or returns `false` for unsupported opcodes.

## Control Flow

Callers pass an incoming IRemoteWinspool opcode to `iremotewinspool_map_opcode()`. The function iterates over `proxy_table` using `ARRAY_SIZE()`. On the first matching `iremotewinspool_opcode`, it stores the mapped `spoolss_opcode` in `*proxy_opcode` and returns `true`. If no entry matches, it leaves the output untouched and returns `false`.

The mapping is intentionally explicit. Comments mark async methods that have no mapping, so unsupported methods fail closed at lookup time instead of accidentally dispatching to a wrong spoolss operation.

## State and Persistence Behavior

The file has no persistent state and no dynamic allocation. `proxy_table` is process-static read-only data after initialization. The only mutation is the caller-provided `proxy_opcode` output pointer on successful lookup.

## Dependencies and Integration Points

The file depends on generated `ndr_winspool.h` and `ndr_spoolss.h` constants and exposes its function through `rpc_server/spoolss/iremotewinspool_util.h`. Its integration point is the spoolss/IRemoteWinspool RPC dispatch path that needs to reuse existing spoolss handlers.

## Risks and Edge Cases

- The lookup is O(n), acceptable for the small table but still dependent on table completeness.
- The function does not NULL-check `proxy_opcode`; callers must pass a valid pointer when they expect a successful mapping.
- Generated opcode renames or additions require manual table updates. Unsupported methods are deliberately absent, so protocol expansion can manifest as false returns.
- The table stores opcodes in `int` but the public API uses `uint16_t`; this assumes generated NDR opcode constants fit in 16 bits.

## Test Signals

Tests should assert known mappings for regular, `EX`, and `2` variants; verify all explicitly unsupported methods return `false`; check that no table entry maps to an unintended spoolss opcode after generated NDR updates; and exercise caller behavior when `iremotewinspool_map_opcode()` fails.
