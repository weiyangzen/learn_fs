# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/compat.h

Header defining the user-space kernel compatibility ABI used by the VNC device and export code.

Key contents:
- Type declarations for `Block`, `Chan`, `Cname`, `Dev`, `Dirtab`, `Proc`, `Ref`, `Rendez`, and `Walkqid`.
- Kernel-style structs for references, rendezvous waiters, channels, canonical names, device operation tables, directory entries, walk results, and process state.
- Channel flags `COPEN` and `CFREE`, error-stack limit `NERR`, name length `KNAMELEN`, and `DEVDOTDOT`.
- Macro `up` mapped to per-process `privup`.
- `waserror()`/`poperror()` macros over `setjmp`.
- Prototypes for device helpers, channel helpers, rendezvous helpers, exporter, and screen initialization.

Role:
- This is the contract that makes copied Plan 9 device code compile as a user-space VNC filesystem.

Risks:
- The header redefines `Rendez` as `KRendez`, so include ordering matters.
- Error handling is macro-based and easy to unbalance.
