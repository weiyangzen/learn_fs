# sources/user-network-fs/samba/source3/librpc/wscript_build

## Purpose
This Waf build script registers source3 NDR subsystems for generated and custom librpc IDL outputs.

## Important APIs, types, and functions
- `SAMBA3_SUBSYSTEM('NDR_LIBNETAPI', ...)` compiles generated libnetapi NDR with `SKIP_NDR_TABLE_libnetapi`.
- `NDR_LIBNET_JOIN`, `NDR_RPC_HOST`, `NDR_OPEN_FILES`, `NDR_SMBXSRV`, `NDR_LEASES_DB`, `NDR_RPCD_WITNESS`, `NDR_SECRETS`, `NDR_PERFCOUNT`, and `NDR_ADS` wire generated files to dependency libraries.
- `NDR_ADS` includes both generated `gen_ndr/ndr_ads.c` and custom `ndr/ndr_ads.c`.

## Control flow
At build time, Waf creates subsystem targets with listed source files and public dependencies. These targets are then consumed by larger Samba binaries/libraries.

## State and persistence behavior
No runtime state. Persistent effect is the build graph and object/library outputs.

## Dependencies and integration points
Dependencies mirror IDL imports: security, server ID, file ID, SMB2 lease, auth, witness, SAMR, LSA, netlogon, NBT, Kerberos, and ODJ. This file connects `source3/librpc/idl/wscript_build` generated outputs to compiled subsystems.

## Risks and edge cases
Dependency omissions can produce link failures or incomplete public headers. Adding a generated IDL without a subsystem or mismatching custom stubs can break builds. Warning allowance on libnetapi may hide generated-code compatibility issues.

## Test signals
Clean configured builds, target-specific rebuilds after IDL changes, link tests for consumers of each NDR subsystem, and dependency pruning checks.
