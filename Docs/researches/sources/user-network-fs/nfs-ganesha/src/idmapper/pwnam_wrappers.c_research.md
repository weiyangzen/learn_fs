<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/idmapper/pwnam_wrappers.c -->
# sources/user-network-fs/nfs-ganesha/src/idmapper/pwnam_wrappers.c

## Purpose
`pwnam_wrappers.c` centralizes passwd/group lookup function selection. It lets NFS-Ganesha use either libc NSS switch APIs or SSSD timeout-aware wrappers behind one stable set of `pwnam_wrappers__*` functions.

## Important APIs, types, and functions
- `getgrouplist_wrapper()` normalizes libc `getgrouplist()` by translating `-1` buffer-too-small returns into `errno = ERANGE`.
- Function pointer globals `getgrouplist_func`, `getpwnam_r_func`, `getpwuid_r_func`, `getgrnam_r_func`, and `getgrgid_r_func` hold the active implementation.
- `pwnam_wrappers__set_implementation()` switches between `PWNAM_IMPLEMENTATION__NSSWITCH` and `PWNAM_IMPLEMENTATION__SSSD`, initializing SSSD before installing SSSD function pointers.
- Thin exported wrappers forward calls to the active function pointers.

## Control flow
The file defaults to NSSwitch/libc implementations at load time. Configuration initialization calls `pwnam_wrappers__set_implementation()`. For NSSwitch, it restores all function pointers to libc wrappers and logs success. For SSSD, it calls `sss_nss_idmap__init()`; on success it installs SSSD-backed functions and logs, and on failure it logs a critical error and returns nonzero without switching.

## State and persistence
The only state is the active set of process-global function pointers. There is no persistence across restart and no per-request state. Once switched, all idmapper and uid-to-group helper calls through the wrappers use the selected backend.

## Dependencies and integration points
The file depends on `pwnam_wrappers.h`, `sss_nss_idmap.h`, libc passwd/group APIs, `errno`, and logging. Higher-level callers in `idmapper.c` and `support/uid2grp.c` use these wrappers instead of directly calling libc, so this file is the integration seam for directory-service implementation choice.

## Risks
- Function pointer updates are unsynchronized; implementation selection is expected to happen during initialization, not concurrently with lookups.
- Failed SSSD initialization leaves previous pointers in place, which is safe for default startup but important if runtime reconfiguration is ever added.
- Return conventions differ between libc `getgrouplist()` and SSSD timeout calls; wrapper normalization is essential for callers that interpret `errno`.
- The comment spelling issue is harmless, but callers depend on the documented `ERANGE`, `ENOENT`, and timeout errno behavior.

## Test signals
- Tests should switch to NSSwitch and verify all exported wrappers call libc-compatible functions.
- SSSD tests should mock successful and failed `sss_nss_idmap__init()` and confirm pointer installation or retention.
- `getgrouplist()` buffer-too-small tests should verify `errno` becomes `ERANGE`.
- Startup tests should confirm idmapper initialization logs and handles selected implementation failures predictably.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/idmapper/pwnam_wrappers.c -->
