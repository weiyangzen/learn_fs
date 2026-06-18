# sources/user-network-fs/samba/source4/torture/rpc/iremotewinspool.c

## Purpose
This file defines the main `rpc.iremotewinspool` suite. It tests the MS-RPRN remote Winspool async endpoint, including object UUID requirements, printer open/close, notification registration, driver-package query/delete negative cases, printer enumeration, printer data, driver directory discovery, and raw response equivalence with classic spoolss.

## Important APIs, Types, And Functions
The suite is registered by `torture_rpc_iremotewinspool()`. Fixture setup parses `IREMOTEWINSPOOL_OBJECT_GUID`, sets it on the binding, opens the print server with `AsyncOpenPrinter`, and discovers architecture through shared helpers. Tests call generated `dcerpc_winspool_*` functions such as `AsyncOpenPrinter`, `AsyncClosePrinter`, `SyncRegisterForRemoteNotifications`, `AsyncEnumPrinters`, `AsyncGetPrinterData`, `AsyncCorePrinterDriverInstalled`, `AsyncDeletePrinterDriverPackage`, and `AsyncGetPrinterDriverDirectory`. `test_compare_spoolss()` uses raw DCE/RPC calls to compare async Winspool and spoolss replies.

## Control Flow
The `printserver` and `handles` tcases use a fixture that opens a server handle and closes it during teardown. Individual tests either open additional handles, register and unregister notifications, perform two-phase buffer-size calls, or validate negative HRESULT/WERROR paths. The `protocol` tcase does not use the fixture; it connects with missing, zero, random, valid, and interface UUID object IDs to verify only `IREMOTEWINSPOOL_OBJECT_GUID` works. The raw comparison builds a spoolss `EnumPrinters` request blob and sends it to both endpoints with different opnums.

## State And Persistence Behavior
Most tests are read-only or handle-scoped. Notification registration creates a transient notification handle that is explicitly unregistered. Delete-driver-package tests attempt to delete core driver packages but expect access denied when inputs are valid enough, so they should not remove installed core drivers. Teardown closes the fixture server handle.

## Dependencies And Integration Points
This file depends on generated Winspool and Spoolss NDR stubs, shared iremotewinspool helper functions, registry string decoding, DCE/RPC object UUID binding support, and named-pipe spoolss transport for cross-interface handle comparison. It integrates with printer server configuration and architecture-specific driver data.

## Risks And Edge Cases
Server behavior depends on advertised client build number; the test expects Windows 2000-era clients to be denied on newer servers. Core-driver installed checks assume the XPS core package is present for x64. Raw reply comparison is strict byte-for-byte and can fail on harmless marshalling or padding differences. Some negative package-delete calls touch real driver package identifiers but expect permission denial.

## Test Signals
Signals include successful fixture open, expected access denied for old build numbers, WERR/HRESULT matches for invalid upload/delete inputs, successful enumeration at levels 1/2/4/5 after insufficient-buffer probes, registry type/value checks for `MajorVersion` and `Architecture`, object-UUID unsupported-type failures, and identical raw response blobs for equivalent enum-printer calls.
