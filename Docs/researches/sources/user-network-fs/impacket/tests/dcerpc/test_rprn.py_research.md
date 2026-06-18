# sources/user-network-fs/impacket/tests/dcerpc/test_rprn.py

Purpose: tests Print Spooler Remote Protocol (`rprn`) named-pipe operations for printer enumeration, open/close, driver-directory lookup, and change notification setup.

Important APIs and functions: `RPRNTests` binds `rprn.MSRPC_UUID_RPRN` over `\PIPE\spoolss`. It covers raw/helper `RpcEnumPrinters`, `RpcOpenPrinter`, `RpcGetPrinterDriverDirectory`, `RpcClosePrinter`, `RpcOpenPrinterEx`, and `RpcRemoteFindFirstPrinterChangeNotificationEx`.

Control flow: `RpcEnumPrinters` uses the normal two-step insufficient-buffer pattern: first call expects `ERROR_INSUFFICIENT_BUFFER`, extracts `pcbNeeded`, allocates a dummy buffer, then retries. Open/close tests obtain server handles for `\\<machine>`. `RpcOpenPrinterEx` builds a `SPLCLIENT_CONTAINER` with machine/user/build/architecture fields. Notification tests open the printer and expect `ERROR_INVALID_HANDLE` for remote change notification.

State and persistence behavior: read-only spooler handle and enumeration operations. No printer configuration is changed. Handles are not always closed after open tests.

Dependencies and integration points: depends on spooler service, named-pipe RPC, Impacket `rprn` helpers, and remote config identity. `hexdump()` is used to print returned printer buffers.

Risks: spooler service may be disabled. Change notification behavior can vary and has security-sensitive history, so run only in controlled environments. Some tests request broad access flags before expecting failure.

Test signals: validates spooler NDR structures, buffer sizing, helper/raw parity, client-info union encoding, handle operations, and NDR64 support.
