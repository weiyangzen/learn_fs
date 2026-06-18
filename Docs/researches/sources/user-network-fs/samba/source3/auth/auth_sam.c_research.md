# sources/user-network-fs/samba/source3/auth/auth_sam.c

## Purpose
This file registers and implements SAM/passdb-backed auth modules. It decides whether a credential belongs to the local SAM/domain for the current server role, then delegates actual password and account validation to `check_sam_security`.

## Important APIs, Types, and Functions
Modules are `sam`, `sam_ignoredomain`, and `sam_netlogon3`. Their check functions are `auth_samstrict_auth`, `auth_sam_ignoredomain_auth`, and `auth_sam_netlogon3_auth`; init functions allocate `auth_methods` records. `auth_sam_init` registers all three.

## Control Flow
`sam_ignoredomain` accepts any non-empty mapped account and ignores domain qualification. `sam` normalizes empty or `.` domains to the local NetBIOS name, rejects UPN-style users on domain members so they can go to the DC, verifies local-name/workgroup ownership based on role, and handles IPA DNS forest matching for DCs. `sam_netlogon3` is restricted to DC roles and only handles the local workgroup or matching IPA forest. All successful ownership checks call `check_sam_security`.

## State and Persistence
This file itself stores no persistent state. It reads server role, workgroup, NetBIOS names, and passdb domain info, while `check_sam_security` may mutate bad-password counters and server-info state.

## Dependencies and Integration Points
It depends on loadparm role/config functions, passdb domain metadata, name comparison helpers, and the shared auth backend registry. It is placed in method chains after anonymous and before or around winbind depending on role.

## Risks and Test Signals
Risks include accepting a domain the local SAM should not service, rejecting valid IPA forest-domain aliases, incorrect fallback to winbind, and fatal exit if `auth_sam` is configured under an AD DC without the inhibit parameter. Tests should cover standalone, domain member, PDC/BDC/IPA DC, UPN users, empty domains, DNS forest matching, and `sam_netlogon3` role enforcement.
