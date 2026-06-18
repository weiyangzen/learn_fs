# sources/user-network-fs/samba/source3/libads/ads_status.h

## Purpose
This header defines the `ADS_STATUS` error container and convenience macros used throughout libads.

## Important APIs and Types
`enum ads_error_type` identifies KRB5, GSS, LDAP, system, and NT error domains. `ADS_STATUS` stores the domain, either integer rc or NTSTATUS, and a GSS minor status. Macros include `ADS_ERROR_LDAP`, `ADS_ERROR_SYSTEM`, `ADS_ERROR_KRB5`, `ADS_ERROR_GSS`, `ADS_ERROR_NT`, `ADS_ERR_OK`, `ADS_SUCCESS`, and `ADS_ERROR_HAVE_NO_MEMORY`.

## Dependencies and Integration Points
It integrates every libads module that returns `ADS_STATUS`, especially LDAP and Kerberos code. It assumes NTSTATUS and LDAP constants are available in including contexts.

## Risks and Test Signals
`ADS_ERR_OK` treats non-NT errors as `rc == 0`, so callers must construct errors in the correct domain. Compile tests should cover macro use in modules with and without LDAP/Kerberos feature macros.
