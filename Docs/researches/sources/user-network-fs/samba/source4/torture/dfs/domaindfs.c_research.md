# sources/user-network-fs/samba/source4/torture/dfs/domaindfs.c

## Purpose
This file defines the domain DFS torture suite. It validates domain referrals, DC referrals for FQDN and NetBIOS names, SYSVOL referrals, unknown-domain errors, subtree referral errors, low referral level errors, and suite registration.

## Important APIs, types, and functions
Local tests are `test_getdomainreferral()`, `test_getdcreferral()`, `test_getdcreferral_netbios()`, `test_getsysvolreferral()`, `test_unknowndomain()`, `test_getsysvolplusreferral()`, and `test_low_referral_level()`. `torture_dfs_init()` creates and registers the `dfs/domain` suite. The file uses `struct dfs_GetDFSReferral`, `struct dfs_referral_resp`, `dfs_cli_do_call()`, referral constants such as `DFS_SERVER_NON_ROOT`, `DFS_FLAG_REFERRAL_DOMAIN_RESP`, `DFS_HEADER_FLAG_STORAGE_SVR`, and torture assertion helpers.

## Control flow
Most tests start by requesting a level-3 domain referral with an empty server name, then use returned `special_name` values to request DC or SYSVOL referrals. FQDN logic chooses a referral containing a dot; NetBIOS logic chooses one without a dot. SYSVOL tests build `<domain>\sysvol`, validate `path_consumed`, storage-server header flags, referral version/type/flags, and expected substrings in `DFS_path` and `netw_address`. The level-4 SYSVOL check expects version 4 and an all-zero service-site GUID. Negative tests expect `NT_STATUS_INVALID_PARAMETER`, `NT_STATUS_NOT_FOUND`, or `NT_STATUS_UNSUCCESSFUL`.

## State and persistence
The tests are read-only protocol calls and do not create files. State comes from live domain DFS configuration returned by the server.

## Dependencies and integration points
The suite depends on `dfs_cli_do_call()` from `common.c`, generated DFS referral NDR structures, and a server configured as or connected to a domain DFS referral provider. It registers under the torture subsystem with one-SMB test cases.

## Risks
The tests assume at least two referral entries in some paths and make selection decisions by looking for dots in returned names. Environments with unusual domain naming, single referral entries, disabled SYSVOL, or different referral-level support may fail for configuration reasons. String assertions are strict and may need updates if referral formatting changes.

## Test signals
Strong signals are nonzero domain referrals, correct path consumption, expected header flags, version 3/4 referral entries, valid special names and expanded names, FQDN/NetBIOS formatting, all-zero service-site GUID for level 4 SYSVOL, and the expected negative NTSTATUS values.
