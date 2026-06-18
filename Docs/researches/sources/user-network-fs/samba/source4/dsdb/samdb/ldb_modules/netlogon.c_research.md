# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/netlogon.c

## Purpose
`netlogon.c` implements CLDAP/netlogon request parsing and response construction against the Samba SAM database. It turns LDAP filter fields into domain/user lookup inputs and fills `struct netlogon_samlogon_response` variants for NT4, NT5, and NT5EX clients, including DC capability flags, site names, domain GUID, DNS names, and optional IPv4 address.

## Important APIs, types, and functions
`fill_netlogon_samlogon_response()` is the main response builder. It accepts SAM LDB context, domain identifiers, user/account-control hints, source address, requested netlogon version bits, loadparm context, output union, and a `fill_on_blank_request` compatibility flag. `parse_netlogon_request()` parses an `LDB_OP_AND` filter into `DnsDomain`, `Host`, `DomainGuid`, `DomainSid`, `User`, `NtVer`, and `AAC` fields.

The code uses DSDB domain/user/trust lookup helpers, loadparm configuration, interface selection helpers, site-name functions, domain functional level checks, and flag mapping from account-control bits to `userAccountControl`.

## Control flow
Response filling first normalizes a trailing dot in the DNS domain. It resolves the target domain by DNS name, NetBIOS name, domain GUID, domain SID, or blank request fallback. GUID input is parsed and encoded into binary filter form; SID input is string-filtered. Any resolved domain must match the local default base DN.

User handling then determines `user_known`. Account-control input is masked to allowed bits, except the `ACB_AUTOLOCK`/`UF_LOCKOUT` path is treated as a DNS trust-domain lookup. Ordinary users are searched under the domain, excluding disabled accounts and matching requested UAC bits. Blank user means known.

The function computes `server_type` flags from local roles and services: DS, PDC, GC, LDAP, KDC, time service, writable/RODC, DC functional level secret-domain flags, and DS version flags through 2016. It determines PDC names, DNS/forest names, server/client sites, closest-site flag, and a best IPv4 address for the source. Finally it zeroes the output union and fills the requested NT5EX-with-IP, NT5EX, NT5, or NT4 response.

`parse_netlogon_request()` requires an AND of equality terms, decodes GUID/SID NDR forms, defaults the domain to local DNS domain if no domain identifier is supplied, and defaults version to `NETLOGON_NT_VERSION_5`.

## State and persistence behavior
This file is read-only with respect to SAM database state. It performs searches and fills caller-owned response structures. It derives network/interface and loadparm state at request time.

## Dependencies and integration points
It integrates CLDAP server handling with SAM LDB, DSDB trust search, site topology, loadparm services, network interface selection, NDR GUID/SID decoding, and netlogon response structures generated from RPC IDL. User-known behavior is intentionally conservative because CLDAP user enumeration has security implications.

## Risks and edge cases
Domain resolution must not answer for non-local domains even if GUID/SID searches find something. Account-control masking is security-sensitive; overly broad filters could leak disabled or wrong-class account existence. IP selection is IPv4-only and falls back to `127.0.0.1` to match Windows behavior. Parser strictness means unexpected filter shapes return `NT_STATUS_UNSUCCESSFUL`.

## Test signals
Test domain lookup by DNS, NetBIOS, GUID, SID, trailing-dot DNS, blank request fallback, and mismatched domain rejection. Verify user-known behavior for disabled users, trust-domain `UF_LOCKOUT` queries, unknown users, and blank users. Check NT4/NT5/NT5EX/NT5EX-with-IP response layouts, server flags for PDC/GC/RODC/services/function levels, site closest flag, IPv4 fallback, and parser failures for non-AND or non-equality filters.
