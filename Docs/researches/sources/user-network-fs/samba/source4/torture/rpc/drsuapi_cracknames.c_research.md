# sources/user-network-fs/samba/source4/torture/rpc/drsuapi_cracknames.c

## Purpose
`drsuapi_cracknames.c` provides extensive DRSUAPI `DsCrackNames` coverage. It validates conversions among SID, GUID, NT4 account, FQDN 1779 DN, canonical, canonical-ex, user principal, service principal, display, DNS-domain, and unknown formats for a temporary joined machine account and well-known directory objects.

## Important APIs, types, and functions
`struct DsCrackNamesPrivate` embeds `struct DsPrivate` and reserves fields for matrix names. `test_DsCrackNames` is the main table-driven test. `test_DsCrackNamesMatrix` first derives one representation for each supported format and then checks conversion consistency across the format matrix. Setup and teardown delegate to `torture_drsuapi_tcase_setup_common` and `torture_drsuapi_tcase_teardown_common`. The code uses `dcerpc_drsuapi_DsCrackNames_r`, LDB DN canonicalization helpers, SID/GUID helpers, generated `drsuapi_DsName*` structures, and well-known SID constants from `security.h`.

## Control flow
The tcase fixture joins the domain and binds via the common DRSUAPI setup. `test_DsCrackNames` first converts the domain SID to NT4, GUID, and FQDN forms, caches domain DNS/GUID/DN state in `DsPrivate`, builds canonical forms through LDB, discovers the joined test DC DN, and constructs UPN/SPN variants. It then iterates a large `crack[]` table with expected status, optional expected result string, expected DNS domain, alternate accepted status, flags such as `DRSUAPI_DS_NAME_FLAG_SYNTACTICAL_ONLY`, and skip markers for Samba4-specific behavior. After table checks it runs the matrix conversion test.

## State and persistence behavior
The file itself does not write directory state; it relies on the temporary machine account created by common setup. It mutates only in-memory fixture fields such as `domain_dns_name`, `domain_guid_str`, `domain_guid`, and `domain_obj_dn`. It allocates many strings under the fixture talloc context. Directory-visible lifecycle is handled by common teardown, which leaves the joined domain account.

## Dependencies and integration points
This module is coupled to `drsuapi.c` setup helpers and `drsuapi.h` state. It depends on LDB for DN parsing/canonicalization, generated DRSUAPI NDR client stubs, Samba torture settings, well-known SID definitions, and domain join helper accessors such as `torture_join_sid`, `torture_join_user_guid`, and `torture_join_netbios_name`. It is registered into the DRS suite by `torture_rpc_drsuapi_cracknames_tcase()`.

## Risks and edge cases
The expected results encode many AD-specific name-cracking details and can vary with server implementation, localization, existing duplicate objects, or service principal configuration. Alternate statuses are accepted for some well-known names, and some display-name tests skip under Samba4. The matrix test compares strings strictly except for known unmappable formats, so case or formatting differences can be noisy. A notable diagnostic wart is a direct `printf("%s\n", n_from[i])` inside matrix preparation.

## Test signals
The strongest signals are per-row `DsNameStatus` values, expected result strings, expected DNS-domain-only responses, and successful full-matrix consistency. Negative coverage includes invalid GUID/SID/NT4/DN/UPN/SPN strings, bogus services, domain-only SPNs, built-in/NT authority SID behavior, and bind GUID not present in the directory.
