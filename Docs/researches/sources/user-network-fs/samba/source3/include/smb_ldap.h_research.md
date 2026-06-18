# sources/user-network-fs/samba/source3/include/smb_ldap.h

## Purpose
`smb_ldap.h` normalizes LDAP and LBER client-library headers and constants across platforms. It provides Samba-local defaults and compatibility aliases for systems with partial or differently named LDAP APIs, and it supplies stub types when LDAP support is not compiled in.

## Important APIs, Types, and Constants
- Conditional platform includes: `lber.h`, `ldap.h`, and optionally `ldap_pvt.h`.
- Compatibility definitions: `LDAP_CONST`, `LDAP_SASL_BIND_IN_PROGRESS`, `LDAPS_PORT`, `LDAP_OPT_SUCCESS`.
- No-LDAP build stubs: `LDAP`, `LDAPMessage`, `LDAPMod`, and `LDAPControl` become `void` aliases; `struct berval` and `struct ldapsam_privates` are forward-declared.
- Timeout and paging constants: `LDAP_DEFAULT_TIMEOUT`, `LDAP_CONNECTION_DEFAULT_TIMEOUT`, `LDAP_PAGE_SIZE`, and `ADS_PAGE_CTL_OID`.
- Password modify extended operation OIDs/tags: `LDAP_EXOP_MODIFY_PASSWD`, `LDAP_TAG_EXOP_MODIFY_PASSWD_ID`, and `LDAP_TAG_EXOP_MODIFY_PASSWD_NEW`.

## Control Flow and State
The file is entirely preprocessor-driven. Control flow is compile-time feature selection based on `HAVE_LBER_H`, `HAVE_LDAP_H`, `HAVE_LDAP`, platform macros, and library-provided OID names. Runtime LDAP connection state is not defined here.

## Persistence Behavior
No persistence is implemented. The constants declared here influence LDAP operations that may modify directory state in other modules.

## Dependencies and Integration Points
It is included by `smbldap.h` and code that talks to OpenLDAP or platform LDAP libraries. It bridges Samba's LDAP abstraction with ADS, ldapsam, passdb, and password-change paths.

## Risks
- Incorrect compatibility aliases can break builds on Solaris, HP-UX, or non-OpenLDAP implementations.
- Stub `void` LDAP types allow non-LDAP builds to parse declarations, but accidental dereference or use outside `#ifdef HAVE_LDAP` would be a compile or runtime design error.
- Timeout/page-size constants affect query responsiveness and memory load when used by LDAP callers.

## Test Signals
LDAP-enabled and LDAP-disabled build matrix coverage is critical. Runtime signals include paged LDAP searches, SASL bind progress handling, LDAPS/TLS startup, and password modify extended operation tests against different LDAP servers.
