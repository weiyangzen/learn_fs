# sources/user-network-fs/samba/source3/rpc_server/wkssvc/srv_wkssvc_nt.c

## Purpose
`srv_wkssvc_nt.c` implements the source3 Workstation Service RPC server. Most legacy WKSSVC operations are explicit stubs, while workstation information, logged-on user enumeration, domain join, and domain unjoin operations have concrete behavior.

## Important APIs, types, and functions
- `struct dom_usr` stores user, domain, and login time for workstation user enumeration.
- `get_domain_userlist()` derives local logged-in users from Samba session records whose remote machine matches the local NetBIOS name.
- `create_wks_info_100()`, `create_wks_info_101()`, and `create_wks_info_102()` allocate workstation info structures from Samba version, NetBIOS name, workgroup, LAN root, and logged-on user count.
- `_wkssvc_NetWkstaGetInfo()` implements levels 100, 101, and 102 with progressively stricter access checks.
- `_wkssvc_NetWkstaEnumUsers()` implements levels 0 and 1 for non-AD-DC source3 service mode and requires Builtin Administrators membership.
- `_wkssvc_NetrJoinDomain2()` and `_wkssvc_NetrUnjoinDomain2()` decode encrypted admin credentials using the RPC session key, build libnet join/unjoin contexts, and call `libnet_Join()` or `libnet_Unjoin()` under root.

## Control flow
`NetWkstaGetInfo` switches on the requested level. Level 100 is available to anonymous callers, level 101 requires authenticated users, level 102 requires Builtin Administrators, and level 502 is denied. `NetWkstaEnumUsers` rejects AD DC mode, checks administrator membership, then returns an empty level-0 user list or a level-1 list built from session records and the configured password server.

`NetrJoinDomain2` validates domain, admin account, encrypted password, and caller privileges. It rejects insecure join and machine-password-passed flags, extracts a 16-byte session key, decodes the WKSSVC password buffer, splits the admin domain/user, creates ADS credentials, populates a `libnet_JoinCtx`, and runs the join as root. `NetrUnjoinDomain2` follows the same credential path, populates a `libnet_UnjoinCtx` using `lp_realm()`, and runs unjoin as root.

## State and persistence behavior
Info and enum calls allocate response structures only. Join/unjoin calls can persistently alter local domain membership, machine account state, and registry-backed Samba configuration when `lp_config_backend_is_registry()` is true. User enumeration reads current Samba session state but does not maintain its own cache.

## Dependencies and integration points
The implementation depends on DCE/RPC call/session state, Samba security tokens and privilege checks, session listing, loadparm values, ADS credential helpers, generated WKSSVC NDR, and libnet join/unjoin APIs. It is built as the `RPC_WKSSVC` subsystem with dependency `LIBNET`.

## Risks and edge cases
- Join/unjoin are high-impact operations and depend on correct privilege checks, session-key extraction, password decoding, and root boundary handling.
- `create_enum_users1()` increments `i` both in the loop and while assigning `other_domains`, which can skip entries and misreport `entries_read`.
- The user enumeration model is an approximation of Windows workstation semantics and only sees local Samba sessions to the local server.
- Many unsupported calls intentionally fault with operation-range behavior, which clients may distinguish from plain `WERR_NOT_SUPPORTED`.

## Test signals
Tests should cover `NetWkstaGetInfo` levels and access denial paths, administrator-only user enumeration, AD DC rejection behavior, join/unjoin invalid parameter and privilege failures, bad session-key handling, encrypted password decode failures, and successful join/unjoin in an isolated domain test environment.
