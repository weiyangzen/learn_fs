# sources/user-network-fs/nfs-ganesha/src/include/pwnam_wrappers.h

## Purpose
This header defines a switchable identity lookup wrapper layer so Ganesha can use libc NSS or direct SSSD-backed implementations for passwd/group resolution.

## Important APIs, Types, And Control Flow
`pwnam_implementation_t` selects `PWNAM_IMPLEMENTATION__NSSWITCH` or `PWNAM_IMPLEMENTATION__SSSD`. Public wrappers include `pwnam_wrappers__set_implementation`, `pwnam_wrappers__getgrouplist`, `pwnam_wrappers__getpwnam_r`, `pwnam_wrappers__getpwuid_r`, `pwnam_wrappers__getgrnam_r`, and `pwnam_wrappers__getgrgid_r`.

## State And Persistence
The selected implementation is process state maintained by the implementation file. Results are caller-provided `passwd`/`group` buffers; no persistence is done.

## Dependencies And Integration Points
It depends on `<grp.h>`, `<pwd.h>`, and system ID types. It feeds idmapper and uid-to-group cache logic, and can route to `sss_nss_idmap.h` when SSSD support is available.

## Risks And Test Signals
Risks include buffer sizing, thread safety, inconsistent NSS/SSSD error codes, and runtime implementation switching. Tests should cover both backends, unknown users/groups, large supplementary group lists, ERANGE retry behavior, and concurrent lookups.
