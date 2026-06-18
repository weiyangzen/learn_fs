# sources/user-network-fs/samba/source3/lib/netapi/localgroup.c

## Purpose

`localgroup.c` implements libnetapi local alias/local-group administration over SAMR and LSA. It was read as a complete 1,390-line file. The module manages local group creation/deletion, info get/set, enumeration across builtin and account domains, and add/delete/set membership for SID- or name-based member inputs.

## Important APIs, Types, and Functions

Entry points include `NetLocalGroupAdd_r/_l`, `NetLocalGroupDel_r/_l`, `NetLocalGroupGetInfo_r/_l`, `NetLocalGroupSetInfo_r/_l`, `NetLocalGroupEnum_r/_l`, `NetLocalGroupAddMembers_r/_l`, `NetLocalGroupDelMembers_r/_l`, `NetLocalGroupGetMembers_r/_l`, and `NetLocalGroupSetMembers_r/_l`. Helpers include `libnetapi_samr_lookup_and_open_alias()`, `libnetapi_samr_open_alias_queryinfo()`, `map_alias_info_to_buffer()`, `map_buffer_to_alias_info()`, `libnetapi_lsa_lookup_names3()`, and shared `NetLocalGroupModifyMembers_r()`.

## Control Flow

Most operations open a SAMR pipe and first search/open aliases in the builtin domain, then fall back to the account domain. Add checks builtin alias existence before creating a domain alias. Get/set info map between `LOCALGROUP_INFO_0`, `LOCALGROUP_INFO_1`, `LOCALGROUP_INFO_1002`, and SAMR alias info levels. Enumeration queries alias counts for both builtin and account domains, enumerates aliases in both, and optionally opens each alias for descriptions at level 1. Membership modification normalizes level 0 SIDs or level 3 names to SIDs, opens the target alias with add/remove/get rights, computes add/delete SID arrays for set mode, then applies SAMR alias member RPC calls.

## State and Persistence Behavior

The module mutates persistent SAM alias objects and alias memberships on the target server. It also performs LSA name-to-SID lookups for level 3 member input. Output buffers are transient talloc arrays attached to `ctx`. SAMR policy handles may be cached by the libnetapi context unless `ctx->disable_policy_handle_cache` forces close.

## Dependencies and Integration Points

Dependencies include generated SAMR and LSA NDR, `rpc_client/cli_lsarpc.h`, LSA open-policy fallback, security SID helpers, `netapi_private` SAMR domain helpers, and public wrappers in `libnetapi.c`. It integrates with builtin-domain and account-domain SAMR helper functions, so behavior depends on domain discovery and policy-handle cache state.

## Risks and Edge Cases

`NetLocalGroupGetMembers_r` returns `WERR_NOT_SUPPORTED`, so the public API is incomplete despite add/delete/set support. `map_alias_info_to_buffer()` uses alias info only for levels that need descriptions; callers must not pass null alias info for level 1/1002. Enumeration uses the same resume handle for builtin and account domain enumeration, which can make resume semantics ambiguous across the combined result set. Membership replacement is multi-step and non-transactional. Level 3 member lookup requires LSA and can fail on ambiguous or unmapped names.

## Test Signals

Tests should cover builtin-vs-domain alias resolution, duplicate alias add returning `WERR_ALIAS_EXISTS`, info levels 0/1/1002, enumeration with descriptions and resume handles, membership add/delete/set with SID and domain\\name inputs, unsupported get-members behavior, and cache enabled/disabled handle cleanup.
