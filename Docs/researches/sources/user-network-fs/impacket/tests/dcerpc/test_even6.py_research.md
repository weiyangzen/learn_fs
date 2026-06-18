# sources/user-network-fs/impacket/tests/dcerpc/test_even6.py

Purpose: tests newer Windows Event Log RPC (`even6`) query/subscription helpers over TCP endpoint-mapped transport.

Important APIs and functions: `EVEN6Tests` binds `even6.MSRPC_UUID_EVEN6`, uses packet privacy, and covers raw/helper `EvtRpcRegisterRemoteSubscription`, `EvtRpcRemoteSubscriptionNext`, `EvtRpcRegisterLogQuery`, `EvtRpcQueryNext`, plus helper `EvtRpcRegisterControllableOperation`, `EvtRpcClearLog`, `EvtRpcExportLog`, and `EvtRpcClose`.

Control flow: subscription tests register a pull subscription on the Security channel with query `*`, fetch up to five records, slice returned event blobs using `EventDataIndices` and `EventDataSizes`, then close the handle. Query tests register a log query and fetch records similarly. Clear/export tests acquire a controllable operation handle, invoke the operation, and close it.

State and persistence behavior: query/subscription paths are read-only. `hEvtRpcClearLog` and `hEvtRpcExportLog` are stateful and potentially destructive/intrusive: they target the Security log and `C:\Security_Log_Exported.evtx`. The source code does not wrap those in expected failure assertions.

Dependencies and integration points: depends on endpoint mapper registration for EVEN6 over TCP, eventlog service, Security log permissions, and Impacket even6 helper structures.

Risks: clear/export operations should be run only in disposable labs. Event availability and permissions vary. Event blobs are assigned to a local variable but not asserted, so tests mainly verify calls do not fail.

Test signals: validates dynamic TCP binding, pull-subscription/query handle lifecycle, packed event buffer index handling, and close helper behavior under NDR/NDR64.
