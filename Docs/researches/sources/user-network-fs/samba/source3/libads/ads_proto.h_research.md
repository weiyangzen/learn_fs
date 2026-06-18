# sources/user-network-fs/samba/source3/libads/ads_proto.h

## Purpose
`ads_proto.h` is the broad libads public prototype header for source3 Active Directory operations, covering ADS structure construction, LDAP operations, SASL/TLS wrapping, machine account management, printer/user/group helpers, SPN management, keytab listing, and trust account password changes.

## Important APIs and Types
It defines `enum ads_sasl_state_e` with plain/sign/seal modes and `struct spn_struct`. It declares `ads_build_path`, `ads_build_dn`, `ads_build_domain`, `ads_init`, `ads_set_sasl_wrap_flags`, `ads_disp_sd`, `ads_keytab_list`, SPN add/delete/list functions, connection functions, LDAP search/modify helpers, machine account create/move/join/leave helpers, domain metadata queries, schema/config path lookups, SASL/TLS wrapper setup, `parse_spn`, and `sync_pw2keytabs`.

## Control Flow and State
As a header it has no state, but it exposes the libads lifecycle: allocate/init `ADS_STRUCT`, connect with credentials or machine account, perform LDAP/Kerberos/SASL operations, then disconnect via `ADS_STRUCT` destructor or explicit calls.

## Dependencies and Integration Points
It depends on `ADS_STRUCT`, `ADS_STATUS`, LDAP-related types, generated RPC/printing types, and credential types. It is a central integration point for `net ads`, domain join, authentication, keytab maintenance, printer publishing, and schema-aware security descriptor display.

## Risks and Test Signals
The header aggregates many modules, so conditional build coverage matters. Tests should compile AD-enabled and AD-disabled feature matrices and verify declarations remain synchronized with source definitions.
