# sources/user-network-fs/samba/source3/libads/ads_struct.c

## Purpose
`ads_struct.c` builds LDAP distinguished-name/domain strings and initializes `ADS_STRUCT`, the central libads connection/config/auth object.

## Important APIs and Functions
Exports are `ads_build_path`, `ads_build_dn`, `ads_build_domain`, `ads_init`, and `ads_set_sasl_wrap_flags`. The static `ads_destructor` disconnects LDAP state when talloc frees an `ADS_STRUCT`.

## Control Flow and State
`ads_build_path` splits a realm using caller separators and builds a field-prefixed path either forward or reverse. `ads_build_dn` converts `AA.BB.CC` to `dc=AA,dc=BB,dc=CC`; `ads_build_domain` lowercases and converts `dc=` DN components back to dotted DNS. `ads_init` talloc-allocates and zeroes the structure, copies realm/workgroup/LDAP server strings, adjusts requested SASL state based on `lp_client_ldap_sasl_wrapping`, sets auth flags, allocates reconnect state, and stores the configured LDAP page size.

## Dependencies and Integration Points
It depends on `ads.h`, loadparm, string helpers, talloc, and LDAP cleanup when available. It is the first step for most AD flows, including machine joins, LDAP queries, keytab refresh, and security descriptor display.

## Risks and Test Signals
`ads_build_path` mixes manual allocation, `asprintf`, `SMB_STRDUP`, and length checks, so allocation and truncation tests are valuable. `ads_build_domain` mutates a duplicated DN and assumes simple `dc=` formatting. `ads_init` silently downgrades SASL state to plain when LDAPS/StartTLS wrapping is configured because the transport wrapper provides protection. Tests should cover null optional strings, SASL flag combinations, destructor disconnect behavior, DN round-trips, and page-size initialization.
