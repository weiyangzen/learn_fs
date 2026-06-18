# sources/user-network-fs/samba/source3/winbindd/winbindd_dsgetdcname.c

## Purpose
Implements async `WINBINDD_DSGETDCNAME`, exposing Windows-style DC locator behavior to winbind clients. It translates libwbclient lookup flags, optionally parses a domain GUID, calls the locator child, and returns a `netr_DsRGetDCNameInfo` projection in the winbind response.

## Important APIs, Types, And Control Flow
`struct winbindd_dsgetdcname_state` stores an optional parsed GUID and returned `dc_info`. `winbindd_dsgetdcname_send()` null-terminates request strings, maps `WBC_LOOKUP_DC_*` flags through `get_dsgetdc_flags()`, parses `domain_guid` with `GUID_from_string()`, and calls `dcerpc_wbint_DsGetDcName_send()` on `locator_child_handle()`. `winbindd_dsgetdcname_done()` combines call status and server result with `any_nt_status_not_ok()`. `winbindd_dsgetdcname_recv()` copies DC UNC/address/type, domain GUID, domain/forest names, flags, and site names into fixed response fields.

## State And Persistence
Only async request-local state is kept. DC locator caching or network discovery state lives below `dsgetdcname()` and the locator child, not in this wrapper.

## Dependencies And Integration Points
Uses generated wbint client stubs, GUID utilities, debug macros, string wrappers, and `_wbint_DsGetDcName()` in `winbindd_dual_srv.c`, which calls Samba's `dsgetdcname()` helper.

## Risks And Test Signals
Flag translation completeness is the main compatibility risk. Invalid GUIDs are silently treated as absent unless they parse to a nonzero GUID. Test every `WBC_LOOKUP_DC_*` flag mapping, empty and malformed GUIDs, forced rediscovery, site-specific lookup, locator child failure, and response truncation for long DNS names.
