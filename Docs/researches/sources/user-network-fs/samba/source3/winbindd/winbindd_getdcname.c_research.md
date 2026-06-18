# sources/user-network-fs/samba/source3/winbindd/winbindd_getdcname.c

## Purpose
Implements legacy async `WINBINDD_GETDCNAME`. It asks the DC locator for a domain controller and returns only the stripped hostname in `response->data.dc_name`.

## Important APIs, Types, And Control Flow
`struct winbindd_getdcname_state` holds returned `netr_DsRGetDCNameInfo`. `winbindd_getdcname_send()` null-terminates `request->domain_name`, logs, and calls `wb_dsgetdcname_send()` with no GUID/site/flags. `winbindd_getdcname_done()` receives `dcinfo`. `winbindd_getdcname_recv()` handles errors and copies `strip_hostname(dcinfo->dc_unc)` into the fixed response field.

## State And Persistence
No local persistent state. DC locator state and cache are delegated to `wb_dsgetdcname_*`.

## Dependencies And Integration Points
Uses winbind request/response structures, `wb_dsgetdcname_send/recv`, generated netlogon types, and string wrapper helpers.

## Risks And Test Signals
Risks are primarily legacy semantics: only the hostname is returned, and no locator flags are exposed. Test unknown domains, locator failure, returned UNC with leading backslashes, very long hostnames, and parity with `DSGETDCNAME` for default lookup.
