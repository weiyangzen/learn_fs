# sources/user-network-fs/impacket/tests/dcerpc/test_par.py

Purpose: tests Print System Asynchronous Remote Protocol (`par`) helper/raw calls over endpoint-mapped TCP.

Important APIs and functions: `PARTests` binds `par.MSRPC_UUID_PAR`, uses packet privacy, and exercises raw/helper `RpcAsyncEnumPrinters`, `RpcAsyncEnumPrinterDrivers`, and `RpcAsyncGetPrinterDriverDirectory`. Raw calls pass `par.MSRPC_UUID_WINSPOOL` as the request UUID where required.

Control flow: enum printers sends a minimal level-0 request. Driver enumeration and driver-directory tests intentionally pass zero buffer and assert `ERROR_INSUFFICIENT_BUFFER`; helper forms perform the helper-managed buffer flow and dump responses.

State and persistence behavior: read-only printer/spooler queries. No printers or drivers are changed.

Dependencies and integration points: depends on spooler service, PAR endpoint mapper registration, Impacket `par` structures, and Windows print subsystem behavior.

Risks: spooler may be disabled or hardened. `ERROR_INSUFFICIENT_BUFFER` is an expected first-call signal; changed server behavior can alter test results. Not-yet-covered add/open/close printer operations would carry more state risk.

Test signals: validates async print RPC marshalling, helper UUID selection, insufficient-buffer error handling, and NDR/NDR64 TCP compatibility.
