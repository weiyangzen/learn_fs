# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/rpc.h

RPC protocol constants and XDR packing helpers for the 9nfs RPC layer.

Key responsibilities:
- Defines ONC/RPC booleans, authentication flavors, message types, accepted/rejected reply status, accept status, reject status, and authentication failure status.
- Provides TCP/UDP protocol number constants.
- Defines 4-byte alignment via `ROUNDUP`.
- Provides byte-order marshaling/unmarshaling macros: `PLONG`, `PPTR`, `PBYTE`, `GLONG`, `GPTR`, and `GBYTE`.

Dependencies:
- Assumes caller-local `dataptr` and `argptr` cursor variables.
- Uses Plan 9 integer aliases such as `uchar` and `ulong`.

Notable risks:
- The macros mutate implicit cursor variables and are not expression-safe abstractions.
- `GPTR(n)` expands to two statements without wrapping, so caller context matters.
