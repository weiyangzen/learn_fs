# sources/user-network-fs/samba/source4/cluster/cluster_private.h

## Purpose
Private header defining the backend vtable for the source4 cluster abstraction and private initialization hooks.

## Important APIs, types, and functions
- `struct cluster_ops` contains function pointers for server ID creation, temporary DB opening, backend handle retrieval, message endpoint initialization, message sending, and backend `private_data`.
- Private prototypes expose `cluster_set_ops()` and `cluster_local_init()` to backend implementations.

## Control flow
The header itself has no control flow. Runtime dispatch is performed by `cluster.c` through this vtable.

## State and persistence behavior
`private_data` lets a backend retain process-local state such as a CTDB context. Persistent database or messaging behavior is delegated to function pointers.

## Dependencies and integration points
Included by `cluster.c` and `local.c`; other real cluster backends can use the same contract to plug into Samba's cluster APIs.

## Risks and edge cases
- There is no versioning or size field on `cluster_ops`, so backend and caller must be compiled against the same contract.
- Function pointer signatures must match exactly; there are no runtime checks for missing methods.

## Test signals
Testing should use a fake backend to ensure every public wrapper calls the expected vtable slot and passes arguments unchanged.
