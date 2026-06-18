# sources/user-network-fs/samba/source3/rpcclient/cmd_iremotewinspool.c

## Purpose
`cmd_iremotewinspool.c` adds rpcclient commands for the IRemoteWinspool async print RPC interface. It can open a printer asynchronously and query whether a core printer driver package is installed.

## Important APIs, types, and functions
- `cmd_iremotewinspool_async_open_printer()` builds a `winspool_AsyncOpenPrinter` request with printer name, datatype `RAW`, a devmode container, user-level client info, and an access mask defaulting to `PRINTER_ALL_ACCESS`.
- `cmd_iremotewinspool_async_core_printer_driver_installed()` builds a `winspool_AsyncCorePrinterDriverInstalled` request with a core driver GUID and architecture defaulting to XPSDRV/x64.
- Both commands call `dcerpc_binding_handle_call()` with `IREMOTEWINSPOOL_OBJECT_GUID`, `ndr_table_iremotewinspool`, and the relevant opnum.
- `iremotewinspool_commands[]` registers the commands as `RPC_RTYPE_WERROR`.

## Control flow
Open-printer validates required printer name, parses optional hex access mask, converts the IRemoteWinspool object GUID, initializes spoolss user-level info from `cli->printer_username`, fills the request, and performs a raw binding-handle call. Core-driver query validates optional arguments, converts both object and driver GUIDs, fills server/environment/version fields, performs the raw call, converts HRESULT failure to `WERROR`, and prints whether the driver is installed.

## State and persistence behavior
The commands are primarily read/query/open operations. Opening a printer creates a remote printer handle returned by the server, but this command only prints success and does not expose follow-up handle operations. No local persistent state is maintained.

## Dependencies and integration points
The file depends on generated Winspool/IRemoteWinspool NDR tables, spoolss initialization helpers, gensec/credentials headers, printer username stored in `rpc_pipe_client`, GUID helpers, HRESULT conversion, and rpcclient command registration.

## Risks and edge cases
- `AsyncOpenPrinter` requests `PRINTER_ALL_ACCESS` by default, which may fail under least-privilege accounts or be too broad for smoke tests.
- The returned printer handle is not closed by this command, so server-side cleanup relies on RPC context teardown.
- GUID parsing failures are mapped to `WERR_NOT_ENOUGH_MEMORY`, which is not semantically precise.
- The usage string for core-driver query says more than four arguments, but the command only consumes up to two user arguments after the command name.

## Test signals
Test against a print server with a known printer using default and reduced access masks, invalid printer names, valid/invalid core driver GUIDs, and alternate architecture strings. Repeated async open calls should be watched for server-side handle cleanup.
