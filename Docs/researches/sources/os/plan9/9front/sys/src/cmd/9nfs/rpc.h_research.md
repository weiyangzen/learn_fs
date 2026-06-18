# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/rpc.h

Shared SunRPC protocol constants and XDR helper macros for 9nfs.

Key contents:
- Defines boolean, auth flavor, message type, accepted/rejected reply, and auth-status enums.
- Defines protocol numbers for TCP and UDP.
- Defines `ROUNDUP()` for 4-byte XDR alignment.
- Defines output macros `PLONG`, `PPTR`, `PBYTE`.
- Defines input macros `GLONG`, `GPTR`, `GBYTE`.

Role:
- Centralizes protocol numbers and serialization primitives used by portmapper, NFS, mount, and RPC support code.

Notable risks:
- Macros depend on caller-local variables named `dataptr` and `argptr`.
- `GPTR(n)` has statement-like expansion and should be used carefully in expression contexts.
