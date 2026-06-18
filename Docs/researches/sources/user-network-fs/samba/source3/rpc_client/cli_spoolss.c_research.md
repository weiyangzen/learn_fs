# sources/user-network-fs/samba/source3/rpc_client/cli_spoolss.c research

## Purpose

`cli_spoolss.c` implements convenience wrappers around generated SPOOLSS RPC client stubs. The wrappers hide common SPOOLSS boilerplate: user-level containers, devmode/security descriptor placeholder containers, WERROR versus NTSTATUS conversion, and the common two-call "insufficient buffer/more data, allocate needed size, retry" pattern used by many printer enumeration and query APIs.

## Important APIs, types, and functions

Open/create APIs are `rpccli_spoolss_openprinter_ex()` and `rpccli_spoolss_addprinterex()`. Query APIs include `rpccli_spoolss_getprinterdriver()`, `rpccli_spoolss_getprinterdriver2()`, `rpccli_spoolss_getprinter()`, `rpccli_spoolss_getjob()`, `rpccli_spoolss_getprinterdata()`, `rpccli_spoolss_enumprinterkey()`, and `rpccli_spoolss_enumprinterdataex()`.

Enumeration APIs include `rpccli_spoolss_enumforms()`, `rpccli_spoolss_enumprintprocessors()`, `rpccli_spoolss_enumprintprocessordatatypes()`, `rpccli_spoolss_enumports()`, `rpccli_spoolss_enummonitors()`, `rpccli_spoolss_enumjobs()`, `rpccli_spoolss_enumprinterdrivers()`, and `rpccli_spoolss_enumprinters()`.

The file uses generated unions and structs such as `spoolss_DriverInfo`, `spoolss_PrinterInfo`, `spoolss_JobInfo`, `spoolss_FormInfo`, `spoolss_PrintProcessorInfo`, `spoolss_PortInfo`, `spoolss_MonitorInfo`, `spoolss_PrinterEnumValues`, `spoolss_SetPrinterInfoCtr`, `spoolss_UserLevelCtr`, and `policy_handle`.

## Control flow

Each wrapper obtains `struct dcerpc_binding_handle *b = cli->binding_handle` and calls the corresponding generated `dcerpc_spoolss_*` function. If the generated call returns a non-OK NTSTATUS, the wrapper returns `ntstatus_to_werror(status)`. Otherwise it returns or processes the WERROR result supplied by the server.

Most query/enumeration wrappers accept an `offered` buffer size. If `offered > 0`, the wrapper allocates a zeroed `DATA_BLOB` of that size and passes it to the generated stub. If the server returns `WERR_INSUFFICIENT_BUFFER` or `WERR_MORE_DATA`, the wrapper reallocates with the returned `needed` size and retries once. Results are returned through generated output pointers such as `info`, `count`, `server_major_version`, `server_minor_version`, `type`, and data buffers.

`rpccli_spoolss_openprinter_ex()` initializes a `spoolss_UserLevel1` from `cli->printer_username`, wraps it in a user-level container, and calls `OpenPrinterEx`. `rpccli_spoolss_addprinterex()` similarly supplies user-level, devmode, and security descriptor containers and uses `cli->srv_name_slash` as the server name.

## State and persistence behavior

The file does not maintain state beyond allocations under the caller's `mem_ctx`. It uses state prepared during pipe binding: `cli->binding_handle`, `cli->printer_username`, and `cli->srv_name_slash`. Returned policy handles and information structures represent server-side printer state, but the local wrappers do not persist anything.

## Dependencies and integration points

Dependencies include generated `ndr_spoolss_c` stubs, `rpc_client/rpc_client.h`, `cli_spoolss.h`, GENSEC/credential headers for client structures, and `init_spoolss.h` for `spoolss_init_spoolss_UserLevel1()`. The wrappers are integration points for Samba utilities and management code that need printer RPCs without manually performing SPOOLSS buffer retries.

## Risks and edge cases

The repeated buffer-sizing pattern trusts server-provided `needed`; a malicious or broken server can force large allocations. Most wrappers retry only once, so a changing server-side object can still return buffer errors to the caller. Some local `DATA_BLOB buffer` variables are only initialized when `offered > 0`, but the code only passes `&buffer` in that case. `rpccli_spoolss_getprinterdata()` always allocates `offered` bytes, so an initial zero-size request may produce allocation behavior that depends on `talloc_zero_array()` semantics.

Conversion from NTSTATUS to WERROR loses some transport detail but matches the declared WERROR interface. Callers must distinguish a returned server WERROR from a converted transport failure only by value.

## Test signals

Tests should cover each wrapper with first-call success, first-call insufficient-buffer/more-data followed by success, generated NTSTATUS failure converted to WERROR, server WERROR failure returned unchanged, zero offered size, very large needed size guard behavior at higher layers, and open/add paths with initialized `printer_username` and `srv_name_slash`.
