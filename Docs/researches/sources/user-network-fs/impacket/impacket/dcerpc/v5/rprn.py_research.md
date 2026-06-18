# sources/user-network-fs/impacket/impacket/dcerpc/v5/rprn.py

## Purpose

`rprn.py` implements a client-side subset of the Print System Remote Protocol [MS-RPRN]. It models print spooler RPC structures and helpers for enumerating printers and drivers, opening and closing printer handles, registering for change notifications, retrieving driver directories, and installing printer drivers.

## Important APIs, Types, And Functions

The module exports `MSRPC_UUID_RPRN`, `DCERPCSessionError`, printer/job/server access constants, change notification flags, printer enumeration flags, notification category constants, and AddPrinterDriverEx file-copy flags. Shared structures include `PRINTER_HANDLE`, `DEVMODE_CONTAINER`, `SPLCLIENT_INFO_1/2/3`, `DRIVER_INFO_1/2`, `DRIVER_INFO_UNION`, `DRIVER_CONTAINER`, `CLIENT_INFO_UNION`, `SPLCLIENT_CONTAINER`, `RPC_V2_NOTIFY_OPTIONS_TYPE`, and `RPC_V2_NOTIFY_OPTIONS`.

RPC calls include `RpcEnumPrinters` opnum 0, `RpcOpenPrinter` opnum 1, `RpcEnumPrinterDrivers` opnum 10, `RpcGetPrinterDriverDirectory` opnum 12, `RpcClosePrinter` opnum 29, `RpcRemoteFindFirstPrinterChangeNotificationEx` opnum 65, `RpcOpenPrinterEx` opnum 69, and `RpcAddPrinterDriverEx` opnum 89. Helpers include `hRpcOpenPrinter`, `hRpcClosePrinter`, `hRpcOpenPrinterEx`, `hRpcRemoteFindFirstPrinterChangeNotificationEx`, `hRpcEnumPrinters`, `hRpcAddPrinterDriverEx`, `hRpcEnumPrinterDrivers`, and `hRpcGetPrinterDriverDirectory`.

## Control Flow

Open helpers null-terminate printer names, attach optional datatype and devmode containers, set access masks, and send requests through `dce.request()`. `hRpcOpenPrinterEx` additionally requires a non-null `SPLCLIENT_CONTAINER`. `hRpcRemoteFindFirstPrinterChangeNotificationEx` requires `pszLocalMachine`, null-terminates it, sets flags/options/local IDs, and sends the notification registration request.

Enumeration and directory helpers use a two-call buffer sizing pattern. The first request sends a null output buffer and zero size. On `ERROR_INSUFFICIENT_BUFFER`, the helper extracts `pcbNeeded` from the decoded exception packet, creates a byte buffer of that size, and retries. `hRpcAddPrinterDriverEx` sends a `DRIVER_CONTAINER` and copy flags directly, which can trigger server-side driver installation.

## State And Persistence Behavior

There is no local disk persistence. Runtime state is carried in remote spooler handles, request/response NDR objects, and temporary output buffers. Remote state can change: `RpcAddPrinterDriverEx` installs or updates printer driver files, `RpcRemoteFindFirstPrinterChangeNotificationEx` registers a server-side notification object, and open/close calls allocate and release handles. Enumeration helpers are read-only from the client perspective.

## Dependencies And Integration Points

The module depends on common dtypes, NDR classes, `system_errors`, `rpcrt.DCERPCException`, and UUID helpers. It integrates with Impacket transports over named pipes such as `\pipe\spoolss` and with `rpcrt.DCERPC.request()` for response decoding and module-specific error handling. `par.py` duplicates much of this module's model for asynchronous print operations.

## Risks And Edge Cases

The print spooler attack surface is historically sensitive. Driver installation and notification registration helpers can be used in offensive workflows when credentials permit. Callers should treat `hRpcAddPrinterDriverEx` as a remote state-changing operation, not as a harmless enumeration helper.

Structure correctness risks mirror `par.py`: `SPLCLIENT_INFO_3` declares `dwFlags` twice, and union tags must be set correctly by callers for driver and client containers. The two-call buffer helpers rely on matching `ERROR_INSUFFICIENT_BUFFER` in exception text and on decoded packets containing `pcbNeeded`; alternate server errors can leave `bytesNeeded` at zero or uninitialized. `checkNullString` assumes string-like input. Placeholder byte buffers are sufficient for NDR output buffers but do not parse returned printer information into typed records.

## Test Signals

Unit tests should verify opnum mappings, helper request layouts, null handling, required parameter exceptions, and two-call retry behavior with fake DCE responses. Structure tests should cover `PRINTER_HANDLE` alignment in NDR32/NDR64, devmode null pointers, driver container union tags, client info union tags, and notification option pointers. Integration tests against a Windows spooler should cover enum printers, open/close, enum drivers, driver directory lookup, notification registration, and a tightly controlled AddPrinterDriverEx path.
