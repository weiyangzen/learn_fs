<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/FSAL/fsal_config.h -->
# sources/user-network-fs/nfs-ganesha/src/include/FSAL/fsal_config.h

## Purpose
`FSAL/fsal_config.h` declares accessor helpers for `struct fsal_staticfsinfo_t`. These helpers expose configured or module-provided filesystem limits and capability flags through a stable FSAL configuration API.

## Important APIs, types, and functions
- `fsal_supports()` tests an `fsal_fsinfo_options_t` capability.
- Scalar accessors include `fsal_maxfilesize()`, `fsal_maxlink()`, `fsal_maxnamelen()`, `fsal_maxpathlen()`, `fsal_maxread()`, `fsal_maxwrite()`, `fsal_umask()`, and `fsal_expiretimeparent()`.
- Capability/mask accessors include `fsal_acl_support()`, `fsal_supported_attrs()`, and `fsal_readdir_mode()`.

## Control flow
FSAL, export, and protocol code pass a static fsinfo object to these functions instead of reading fields directly. The implementation can apply defaults, option masks, or configured overrides consistently.

## State and persistence
The header has no state. It reads static filesystem info, which is runtime configuration associated with FSAL modules or exports and may reflect persistent export configuration.

## Dependencies and integration points
The header relies on FSAL API types being available to includers. It integrates FSAL module capabilities with protocol responses such as FSINFO, PATHCONF, access limits, readdir behavior, and attribute support.

## Risks
- The header has no include guard and no direct include of FSAL type definitions; it assumes include context.
- Consumers that bypass accessors may observe different behavior from code using normalized helper results.
- Capability option semantics need to stay aligned with `fsal_staticfsinfo_t` field layout.

## Test signals
- Compile tests should include this header through normal FSAL include paths and directly if that is expected.
- Configuration tests should verify every accessor returns correct defaults, overrides, and capability-mask results.
- Protocol integration tests should compare NFS FSINFO/PATHCONF-like replies against FSAL static fsinfo.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/FSAL/fsal_config.h -->
