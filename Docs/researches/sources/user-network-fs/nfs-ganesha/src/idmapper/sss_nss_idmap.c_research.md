<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/idmapper/sss_nss_idmap.c -->
# sources/user-network-fs/nfs-ganesha/src/idmapper/sss_nss_idmap.c

## Purpose
`sss_nss_idmap.c` dynamically loads SSSD's `libsss_nss_idmap.so.0` and adapts its timeout-aware NSS lookup functions to the same signatures used by Ganesha's passwd/group wrapper layer.

## Important APIs, types, and functions
- Function pointer typedefs model SSSD timeout APIs for `getpwnam`, `getpwuid`, `getgrnam`, `getgrgid`, and `getgrouplist`.
- Static state includes `is_inited`, `handle`, `sssd_flags`, and `sssd_timeout`.
- Global resolved symbols include `sss_nss_getpwnam_timeout`, `sss_nss_getpwuid_timeout`, `sss_nss_getgrnam_timeout`, `sss_nss_getgrgid_timeout`, and `sss_nss_getgrouplist_timeout`.
- `sss_nss_idmap__init()` reads directory-service SSSD options, computes flags and timeout in milliseconds, `dlopen()`s the library, resolves required symbols, and marks initialized.
- `sss_nss_idmap__getpwnam()`, `sss_nss_idmap__getpwuid()`, `sss_nss_idmap__getgrnam()`, and `sss_nss_idmap__getgrgid()` forward to the SSSD functions with configured flags and timeout.
- `sss_nss_idmap__getgrouplist()` adapts SSSD's `0` or errno return convention to libc-like `getgrouplist()` behavior by setting `errno` and returning `-1` on failure or `*ngroups` on success.

## Control flow
Initialization first computes runtime options from `nfs_param.directory_services_param`: `sssd_implementation_skip_cache` selects `SSS_NSS_EX_FLAG_NO_CACHE`, and `sssd_implementation_timeout` is converted from seconds to milliseconds. If already initialized, the function returns success after refreshing config-derived fields. If a prior `dlopen()` succeeded but later symbol resolution failed, `handle` remains non-NULL and future init attempts return failure immediately.

On first successful initialization, the file loads `libsss_nss_idmap.so.0` lazily and resolves all required timeout symbols. Public wrapper calls fatal if invoked before successful init, then delegate to the resolved function pointer with `sssd_flags` and `sssd_timeout`.

## State and persistence
State is process-local dynamic-linker state plus cached configuration flags. The library handle is not closed in this file. No lookup data is persisted; SSSD's own cache behavior is controlled by the flags passed to each call.

## Dependencies and integration points
The file depends on `dlopen()`, `dlsym()`, SSSD NSS idmap ABI names, Ganesha logging, and global `nfs_param`. It is selected by `pwnam_wrappers__set_implementation(PWNAM_IMPLEMENTATION__SSSD)` and then services idmapper and uid2grp lookups.

## Risks
- Partial initialization is sticky: after `dlopen()` succeeds but a required `dlsym()` fails, `handle` remains set and later retries return failure without closing/retrying.
- Public calls use `LogFatal()` on missing init; caller ordering must guarantee successful init before function pointer installation.
- The file defines SSSD flag constants locally. If upstream SSSD ABI changes, mismatches may not be caught at compile time.
- Timeout unit conversion assumes the configuration value is in seconds and SSSD wants milliseconds.
- Dynamic loading failures are runtime deployment issues; packages must include the expected shared library when SSSD mode is configured.

## Test signals
- Dynamic-link tests should cover missing library, missing individual symbols, successful symbol resolution, and the sticky partial-failure path.
- Configuration tests should verify skip-cache flag selection and timeout conversion.
- Wrapper tests should ensure `getgrouplist` converts SSSD error codes to `errno` plus `-1`, and success returns the group count.
- Integration tests should verify Ganesha startup refuses or falls back correctly when SSSD mode cannot initialize.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/idmapper/sss_nss_idmap.c -->
