# sources/user-network-fs/samba/source3/rpc_client/util_netlogon.h

## Purpose
`util_netlogon.h` declares Netlogon copy and validation mapping helpers for authentication and RPC client code.

## Important APIs, Types, And Functions
It declares deep-copy helpers for `netr_SamBaseInfo`, `netr_SamInfo3`, `netr_SamInfo6`, and `netr_DsRGetDCNameInfo`, plus conversion helpers between `union netr_Validation` levels and concrete SamInfo3/SamInfo6 structures.

## Control Flow
No logic is implemented in the header. The API follows NTSTATUS-returning C helper conventions with talloc contexts and output pointers.

## State And Persistence
The header stores no state. Implementations allocate transient copied structures for callers.

## Dependencies And Integration Points
Consumers must include generated Netlogon types. The helpers are integrated with winbind, auth server-info conversion, rpcclient Netlogon commands, and DC locator handling.

## Risks
The contract is limited to validation levels 3 and 6. Callers must check NTSTATUS before using output pointers and must manage talloc ownership.

## Test Signals
Compile coverage plus Netlogon validation mapping tests, auth server-info conversion tests, and DC locator copy tests validate the API.
