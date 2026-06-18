# sources/user-network-fs/samba/source3/libads/ads_status.c

## Purpose
`ads_status.c` centralizes libads error construction, conversion to NTSTATUS, and human-readable error string formatting across LDAP, Kerberos, GSSAPI, system errno, and NTSTATUS domains.

## Important APIs and Functions
Exports are `ads_build_error`, `ads_build_nt_error`, `ads_ntstatus`, `ads_errstr`, and, under Kerberos support, `gss_err_to_ntstatus`. They operate on `ADS_STATUS` from `ads_status.h`.

## Control Flow and Behavior
The builders validate error-domain usage and fall back to system errors if called with the wrong constructor. `ads_ntstatus` switches on `error_type`, mapping errno through `map_nt_error_from_unix`, LDAP timeout to `NT_STATUS_IO_TIMEOUT`, generic LDAP to `NT_STATUS_LDAP`, Kerberos through `krb5_to_nt_status`, and NT errors directly. `ads_errstr` picks the corresponding string source; for GSS it calls `gss_display_status` for both major and minor codes and returns a talloc string.

## State and Dependencies
There is no durable state. Dependencies are conditional LDAP, Kerberos, and GSS APIs, Samba NTSTATUS mappings, talloc, and DEBUG.

## Risks and Test Signals
`ads_errstr` returns talloc stack memory for GSS strings, so callers must not assume permanent storage. Constructor misuse is logged but not fatal. Tests should cover each `enum ads_error_type`, LDAP timeout mapping, success detection, GSS major/minor formatting, and disabled LDAP/Kerberos compile paths.
