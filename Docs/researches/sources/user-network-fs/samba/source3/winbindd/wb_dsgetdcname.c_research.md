# sources/user-network-fs/samba/source3/winbindd/wb_dsgetdcname.c

## Purpose
This async helper locates a domain controller through winbind child RPC and provides one-hour gencache helpers for `netr_DsRGetDCNameInfo` results.

## Important APIs, Types, And Functions
`wb_dsgetdcname_send` and `wb_dsgetdcname_recv` wrap `dcerpc_wbint_DsGetDcName`. Cache functions are `wb_dsgetdcname_gencache_set` and `wb_dsgetdcname_gencache_get`. `dcinfo_parser` deserializes cached NDR blobs.

## Control Flow
The send path rejects `BUILTIN` and, on non-AD-DC local SAM domains, returns domain-controller-not-found to avoid loopback connects. DC processes use the locator child and may replace a NetBIOS domain with DNS alt name for AD trusts. Non-DC processes delegate to the own-domain child. The optional GUID is copied to work around const generated-code signatures. Cache set serializes dcinfo to an NDR blob under uppercase `DCINFO/<domain>` and stores it for 3600 seconds. Cache get parses the same key, ignores expired entries, deserializes, and returns not-found when absent.

## State And Persistence
Request state is tevent-local. Cached DC info persists in Samba gencache for one hour.

## Dependencies And Integration
It depends on winbind domain role helpers, locator/domain child handles, generated RPC stubs, Netlogon NDR types, and gencache. It is part of winbind DC locator behavior.

## Risks And Test Signals
Test BUILTIN rejection, local SAM on non-AD-DC, AD DC trust name replacement, GUID and no-GUID calls, RPC status/result failures, cache expiry, NDR serialization failures, and corrupted cache blobs. Role-specific behavior is important because the selected child handle changes with `IS_DC` and `IS_AD_DC`.
