# sources/user-network-fs/samba/source3/include/ntdomain.h

## Purpose
`ntdomain.h` is a small compatibility/include boundary for NT domain RPC concepts that were moved out of broader SMB headers. It keeps the GENSEC context forward declaration and RPC pipe definitions available to source3 NT domain code.

## Important APIs, Types, And Control Flow
The file forward-declares `struct gse_context` and includes `rpc_server/rpc_pipes.h`. It declares no functions, macros beyond the include guard, or runtime data structures of its own.

## State And Persistence
There is no state or persistence in this header. It influences compilation dependencies by making RPC pipe types visible without pulling unrelated SMB declarations into each consumer.

## Dependencies And Integration Points
It integrates with RPC server pipe code, domain authentication flows, and GSS/GENSEC-related authentication contexts. Its value is mostly dependency hygiene for source3 domain and RPC code.

## Risks And Test Signals
Risks are include-order and dependency risks: removing the forward declaration or include can break consumers relying on transitive visibility, while adding heavy includes can increase coupling. Test signals are build coverage of source3 RPC/domain files, include-what-you-use checks, and authentication/RPC pipe compile tests with GENSEC-enabled and reduced configurations.
