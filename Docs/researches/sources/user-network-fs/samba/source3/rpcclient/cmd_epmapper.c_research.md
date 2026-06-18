# sources/user-network-fs/samba/source3/rpcclient/cmd_epmapper.c

## Purpose
`cmd_epmapper.c` implements rpcclient endpoint mapper commands. `epmmap` maps an interface and transport to endpoint towers, and `epmlookup` enumerates registered endpoint mapper entries.

## Important APIs, types, and functions
- `cmd_epmapper_map()` resolves an NDR interface name via `ndr_table_list()`, parses a transport name and optional object UUID, builds a tower from a synthetic binding, calls `dcerpc_epm_Map()`, converts returned towers back to bindings, and prints them.
- `cmd_epmapper_lookup()` repeatedly calls `dcerpc_epm_Lookup()` one entry at a time, prints object GUID, binding string, and annotation, and stops on `NO_MORE_ENTRIES`.
- `epmapper_commands[]` registers `epmmap` and `epmlookup` as `RPC_RTYPE_NTSTATUS` against `ndr_table_epmapper`.

## Control flow
`epmmap` defaults to `lsarpc` over `ncacn_np`, validates the interface and transport, builds a tower using a placeholder binding, sends the map request, checks endpoint mapper result codes, and iterates returned tower pointers. `epmlookup` maintains an `entry_handle` across loop iterations and frees a temporary context per returned entry.

## State and persistence behavior
Both commands are read-only and keep only transient local lookup state. The remote endpoint mapper's registration database is not modified.

## Dependencies and integration points
The file depends on generated EPMAPPER stubs, Samba binding parse/build helpers, NDR interface table registration, GUID helpers, and endpoint mapper status constants.

## Risks and edge cases
- `epmmap` relies on the local NDR table name matching user input; unknown names fail locally before contacting the server.
- The synthetic binding string `ncacn_np:127.0.0.1[0]` is only a tower construction seed.
- `epmlookup` always returns `NT_STATUS_OK` after printing lookup errors, so automated callers need to parse output to detect partial failures.

## Test signals
Run `epmlookup` against Samba and Windows endpoint mappers and compare known service annotations/bindings. Run `epmmap` for registered interfaces over supported transports, plus negative tests for unknown interface, unknown transport, and invalid UUID.
