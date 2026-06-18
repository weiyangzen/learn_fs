# sources/user-network-fs/samba/source3/librpc/idl/wscript_build

## Purpose
This Waf build script defines how source3-specific IDL files are processed by PIDL into generated NDR parsers, headers, clients, and Python bindings.

## Important APIs, types, and functions
- `topinclude` points PIDL at the source IDL include directory.
- The first `SAMBA_PIDL_LIST` builds `open_files`, `perfcount`, `secrets`, `smbXsrv`, `leases_db`, and `rpcd_witness` with headers, NDR parsers, client code, and Python output.
- The second list builds `libnetapi` and `rpc_host` with headers and parsers, no generated tables.
- The third list builds `libnet_join` and `ads` with both source IDL and generated include directories, no generated tables.

## Control flow
At build time, Waf evaluates the script and schedules PIDL invocations. Generated output goes to `../gen_ndr`.

## State and persistence behavior
The script has no runtime state. Its persistent effect is generated source/header output under the build tree, which downstream `wscript_build` subsystem definitions compile.

## Dependencies and integration points
It depends on Waf's Samba build helpers and PIDL. `absinclude` references `bin/default/include` for generated configuration includes needed by `ads.idl`/`libnet_join.idl`.

## Risks and edge cases
Missing `generate_tables=False` would change generated artifacts for local-only interfaces. Include path ordering matters for IDL imports. Adding an IDL here without matching subsystem wiring in `source3/librpc/wscript_build` can break builds.

## Test signals
Run configured builds from clean trees, verify generated `gen_ndr` files exist, and check both table-generating and no-table interfaces compile with expected dependencies.
