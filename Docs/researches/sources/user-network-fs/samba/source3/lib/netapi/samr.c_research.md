# Research: sources/user-network-fs/samba/source3/lib/netapi/samr.c

Purpose: shared SAMR helper implementation for opening and closing domain, builtin-domain, and connect policy handles used by NetAPI user/group/localgroup operations. It centralizes SAMR connection setup and context-level handle caching.

Important APIs/functions: `libnetapi_samr_open_domain` opens or reuses a SAMR connect handle, enumerates domains, skips the builtin domain, looks up the selected domain SID, opens that domain, and caches handles/masks/SID. `libnetapi_samr_open_builtin_domain` opens or reuses the builtin domain using `global_sid_Builtin`. `libnetapi_samr_close_domain_handle`, `libnetapi_samr_close_builtin_handle`, `libnetapi_samr_close_connect_handle`, and `libnetapi_samr_free` close cached handles through `dcerpc_samr_Close`.

Control flow: each open function first checks cached handles in `libnetapi_private_ctx` and reuses them only when the cached access mask covers the requested mask. If a cached handle is insufficient it is closed and reopened. Domain open performs `dcerpc_try_samr_connects`, `samr_EnumDomains`, first non-builtin-domain selection, `samr_LookupDomain`, and `samr_OpenDomain`. Builtin open performs connect and `samr_OpenDomain` with the builtin SID.

State and persistence: policy handles, masks, SAMR pipe client, domain name, and domain SID are cached in the context. The cache is process-local but represents server-side RPC handles that must be closed. No SAM database changes are made here; higher-level callers use the opened handles for persistent account/group changes.

Dependencies/integration: depends on `rpc_pipe_client`, generated SAMR client stubs, `dcerpc_try_samr_connects`, LSA string initialization, Samba security SID constants, and private context shape from `netapi_private.h`. It supports user, group, localgroup, display, and modals code outside this work item.

Risks: domain selection uses the first enumerated non-builtin domain, which may be ambiguous on unusual servers. Cached `domain_name` points into data allocated under the context/RPC call memory and must not outlive the context. Close helpers only close handles equal to the cached handles; closing copies or unrelated handles is ignored, which protects the cache but can leak if callers expected arbitrary close behavior. `priv->samr.cli` must remain valid when close helpers run.

Test signals: tests should open the same domain with identical and wider masks, verify reuse/reopen behavior, simulate no non-builtin domain, verify builtin handle open, and run `libnetapi_samr_free` under leak/handle-close instrumentation. Integration tests should cover Samba standalone/domain-member/AD modes.
