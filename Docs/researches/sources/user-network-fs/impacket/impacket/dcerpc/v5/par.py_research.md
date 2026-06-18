# sources/user-network-fs/impacket/impacket/dcerpc/v5/par.py

## Purpose

`par.py` implements a client-side subset of the Print System Asynchronous Remote Protocol [MS-PAR]. It mirrors much of the synchronous printer binding shape from `rprn.py`, but uses async spooler opnums and usually sends requests with the WINSPOOL object UUID. The implemented surface opens and closes printer handles, enumerates printers and printer drivers, retrieves driver directories, and installs printer drivers.

## Important APIs, Types, And Functions

The module exports `MSRPC_UUID_PAR`, `MSRPC_UUID_WINSPOOL`, `DCERPCSessionError`, printer access constants, change notification flags, enumeration flags, notification categories, and driver-copy flags. It defines shared print structures such as `PRINTER_HANDLE`, `DEVMODE_CONTAINER`, `SPLCLIENT_INFO_1/2/3`, `DRIVER_INFO_1/2`, `DRIVER_INFO_UNION`, `DRIVER_CONTAINER`, `CLIENT_INFO_UNION`, `SPLCLIENT_CONTAINER`, and async notify option structures.

RPC calls include `RpcAsyncOpenPrinter` opnum 0, `RpcAsyncClosePrinter` opnum 20, `RpcAsyncEnumPrinters` opnum 38, `RpcAsyncAddPrinterDriver` opnum 39, `RpcAsyncEnumPrinterDrivers` opnum 40, and `RpcAsyncGetPrinterDriverDirectory` opnum 41. Helpers include `hRpcAsyncOpenPrinter`, `hRpcAsyncClosePrinter`, `hRpcAsyncEnumPrinters`, `hRpcAsyncAddPrinterDriver`, `hRpcAsyncEnumPrinterDrivers`, and `hRpcAsyncGetPrinterDriverDirectory`.

## Control Flow

Open and close helpers create a request, populate handles and optional containers, and call `dce.request(request, MSRPC_UUID_WINSPOOL)`. `hRpcAsyncOpenPrinter` requires a non-null client info container and initializes `pDevModeContainer.pDevMode` to `NULL` when no devmode is supplied.

Enumeration helpers follow the common Windows RPC two-call buffer pattern. They first send a request with a null output buffer and zero buffer size. If the server returns `ERROR_INSUFFICIENT_BUFFER`, they read `pcbNeeded` from the decoded error packet, allocate a placeholder byte buffer of that size, and send the request again. Driver enumeration and driver directory lookup use the same pattern. `hRpcAsyncAddPrinterDriver` sends a filled `DRIVER_CONTAINER` and file-copy flags directly.

## State And Persistence Behavior

There is no disk persistence. Runtime state is in printer context handles, caller-supplied driver/client containers, and temporary byte buffers. Remote side effects can be significant: `RpcAsyncAddPrinterDriver` installs printer driver files on the remote spooler, and open/close helpers create and release server-side handles. Enumeration helpers are read-oriented but can disclose printer and driver inventory.

## Dependencies And Integration Points

The module depends on common dtypes, NDR classes, `system_errors`, `rpcrt.DCERPCException`, and UUID helpers. It integrates with the DCE runtime through `dce.request` and object UUID routing. Its structures and helper patterns are intentionally close to `rprn.py`, so tests and callers often compare the async and sync spooler implementations.

## Risks And Edge Cases

There are correctness hazards in the IDL model. `SPLCLIENT_INFO_3` declares `dwFlags` twice, which can overwrite or obscure the first value in Impacket field access. `OPNUMS` maps opnum 39 to `(RpcAsyncAddPrinterDriver, RpcAsyncAddPrinterDriver)` instead of the response class, which can break generic dispatch or server-side use of the table. Error text says `RPRN SessionError`, which is confusing for PAR failures.

The two-call helpers depend on string matching `ERROR_INSUFFICIENT_BUFFER` in exception text and on `e.get_packet()['pcbNeeded']` being available. If the server returns success with no data, a different error, or an undecodable error packet, `bytesNeeded` may remain zero or unbound in some paths. `checkNullString` assumes string-like input, and helpers use placeholder `b'a'` buffers rather than typed result structures.

## Test Signals

Unit tests should verify opnum mappings, especially opnum 39, and serialize every helper with a fake DCE object. Buffer-sizing tests should simulate `ERROR_INSUFFICIENT_BUFFER` packets and successful second calls. Structure tests should cover `DRIVER_CONTAINER` union tags, `SPLCLIENT_CONTAINER` union tags, `NULL` devmode behavior, and the duplicate `dwFlags` field. Integration tests need a Windows spooler and should validate open, enum printers, enum drivers, get driver directory, close, and guarded driver-install scenarios.
