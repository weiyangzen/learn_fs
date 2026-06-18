# sources/user-network-fs/samba/source4/torture/rpc/srvsvc.c

## Purpose

`srvsvc.c` is the Samba torture suite for the Server Service RPC interface. It validates character-device, queue, connection, file, session, share, server, disk, transport, remote time-of-day, and name-validation operations under administrative and anonymous credentials.

## Important APIs, Types, and Functions

The file consists of focused test helpers for each SRVSVC family: `test_NetCharDevEnum/GetInfo/Control`, `test_NetCharDevQEnum/GetInfo`, `test_NetConnEnum`, `test_NetFileEnum`, `test_NetSessEnum`, `test_NetShareGetInfo`, `test_NetShareAddSetDel`, `test_NetShareEnumAll`, `test_NetShareEnum`, `test_NetSrvGetInfo`, `test_NetDiskEnum`, `test_NetTransportEnum`, `test_NetRemoteTOD`, and `test_NetNameValidate`. The suite factory `torture_rpc_srvsvc()` creates one authenticated admin tcase and one anonymous tcase.

## Control Flow

Enumeration functions build the appropriate info-control union for each level, call the generated `dcerpc_srvsvc_*_r()` request, and either assert exact expected errors or log non-fatal unexpected results depending on historical tolerance. Share enumeration tests compare anonymous versus admin expectations and, for level 2 results, drill into each returned share through `NetShareGetInfo` and `NetShareCheck`. `test_NetShareAddSetDel()` creates a temporary `testshare`, applies multiple `NetShareSetInfo` levels, reads back level 502 details, checks fields, and deletes the share. `test_NetNameValidate()` probes accepted maximum lengths and invalid ASCII characters for name types 1 through 13 under two flag values.

## State and Persistence Behavior

Most tests are read-only enumerations. `test_NetShareAddSetDel()` mutates server share configuration by adding, changing, and deleting `testshare`; it is marked `dangerous`. If deletion fails, the test share can remain configured. Name validation allocates temporary strings only. Resume handles are local variables and are not persisted.

## Dependencies and Integration Points

The file depends on generated `ndr_srvsvc_c.h` client stubs, `torture_rpc.h` testcase helpers, server name binding through `dcerpc_server_name()`, and server-side share/session/file state. Anonymous access tests depend on the torture framework's anonymous RPC tcase setup.

## Risks and Edge Cases

Some SRVSVC calls are obsolete or may be unimplemented on a target server. The test often logs non-OK WERRORs rather than failing for enumeration families, so it is better at compatibility smoke coverage than strict conformance for those calls. `test_NetShareAddSetDel()` uses a Windows path `C:\` and assumes permissions allow share mutation. The final delete assertion mistakenly checks `a.out.result` instead of `d.out.result`, which can mask a failed delete result after a successful add.

## Test Signals

Passing admin tests show broad SRVSVC availability, share information access, share mutation support, and name validation behavior. Passing anonymous tests verify expected access-denial boundaries for level 2/501/502 share data while allowing low-detail share enumeration.
