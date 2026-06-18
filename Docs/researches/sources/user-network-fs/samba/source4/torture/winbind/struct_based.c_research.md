<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/winbind/struct_based.c -->
# sources/user-network-fs/samba/source4/torture/winbind/struct_based.c

## Purpose

This file implements `winbind.struct`, a torture suite for the legacy struct-based winbind client protocol. It sends `WINBINDD_*` operations through `wbcRequestResponse()` and validates interface versioning, ping, configuration identity, trusted-domain enumeration, domain-controller lookup, passwd enumeration, user/group listing, name/SID round trips, and invalid SID lookup behavior.

## Important APIs, Types, and Functions

- `DO_STRUCT_REQ_REP_EXT()` maps libwbclient errors into NSS-style statuses and enforces strict or warning-only expectations.
- `winbind_separator()`, `get_winbind_domain()`, `get_trusted_domains()`, `get_user_list()`, and `get_group_list()` are shared request/parse helpers.
- `torture_winbind_struct_interface_version()`, `ping()`, `info()`, `priv_pipe_dir()`, `netbios_name()`, `domain_name()`, and `check_machacc()` validate basic daemon metadata and machine account state.
- `torture_winbind_struct_list_trustdom()`, `domain_info()`, `getdcname()`, and `dsgetdcname()` exercise trust and DC discovery.
- `torture_winbind_struct_setpwent()`, `getpwent()`, and `endpwent()` exercise NSS passwd enumeration operations.
- `lookup_name_sid_list()` and `torture_winbind_struct_lookup_name_sid()` validate `LOOKUPNAME` and `LOOKUPSID` as inverses for listed users/groups and check invalid inputs.
- `torture_winbind_struct_init()` registers all tests.

## Control Flow

Most tests zero a `winbindd_request` and `winbindd_response`, issue one request via the macro, then assert fields or parse `extra_data`. Trust parsing expects newline-separated records in `NETBIOS\DNS\SID` form and verifies at least BUILTIN plus the local domain. User/group parsing consumes comma-separated extra data. Lookup tests enumerate known users/groups, split domain-qualified names using the configured separator or UPN fallback, perform name-to-SID and SID-to-name calls, then compare the reconstructed name case-insensitively. Some tests use a `strict mode` torture option: without strict mode, environment-sensitive failures become warnings.

## State and Persistence Behavior

The tests do not modify persistent domain state. They do exercise winbind daemon cached state, NSS enumeration cursor state (`SETPWENT`/`GETPWENT`/`ENDPWENT`), and machine-account verification. Response `extra_data.data` returned by winbind is freed with `SAFE_FREE()` in most parsing helpers.

## Dependencies and Integration Points

Dependencies include libwbclient internals, `winbind_struct_protocol.h`, `winbind_nss_config.h`, Samba security SID helpers, Netlogon constants, loadparm settings, and PAM error mapping. The suite is included by `torture/winbind/winbind.c` and built into `TORTURE_WINBIND`.

## Risks and Edge Cases

The tests are sensitive to configured workgroup, winbind separator, trusts, domain mode, and availability of users/groups. `get_group_list()` has a diagnostic string typo for zero entries, and `getpwent()` has Samba3-specific tolerance because some Samba3 deployments return success without an entry. Parsing assumes trust lines contain two backslashes and that BUILTIN is first. The `getdcname`/`dsgetdcname` tests may not exercise anything in small or non-AD environments unless strict mode is enabled.

## Test Signals

Strong pass signals are matching interface version, stable ping loop, correct separator/netbios/domain metadata, valid machine-account status, trust/domain-info SID consistency, non-empty and count-matched group lists, successful passwd enumeration when expected, reversible name/SID lookup for all listed principals, and `NSS_STATUS_NOTFOUND` for invalid lookups.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/winbind/struct_based.c -->
