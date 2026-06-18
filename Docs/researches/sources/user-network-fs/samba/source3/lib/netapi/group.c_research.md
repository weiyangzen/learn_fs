# sources/user-network-fs/samba/source3/lib/netapi/group.c

## Purpose

`group.c` implements libnetapi global/domain group management over SAMR. It was read as a complete 1,852-line file. The file supports group create/delete, get/set info, add/delete a user, enumerate groups, enumerate group users, and replace a group's users.

## Important APIs, Types, and Functions

Public internal entry points are `NetGroupAdd_r/_l`, `NetGroupDel_r/_l`, `NetGroupSetInfo_r/_l`, `NetGroupGetInfo_r/_l`, `NetGroupAddUser_r/_l`, `NetGroupDelUser_r/_l`, `NetGroupEnum_r/_l`, `NetGroupGetUsers_r/_l`, and `NetGroupSetUsers_r/_l`. Helpers include `map_group_info_to_buffer()` and `convert_samr_disp_groups_to_GROUP_INFO_{0,1,2,3}_buffer()`. The code uses SAMR functions such as `CreateDomainGroup`, `LookupNames`, `OpenGroup`, `QueryGroupInfo`, `SetGroupInfo`, `QueryGroupMember`, `LookupRids`, `AddGroupMember`, `DeleteGroupMember`, `QueryDisplayInfo2`, and `DeleteDomainGroup`.

## Control Flow

Most functions open a SAMR pipe, open the account domain with access rights tailored to the operation, look up the group name to a RID, verify the SID name type, open the group handle, perform the operation, then close handles when policy-handle caching is disabled. `NetGroupAdd_r` creates a group and optionally sets comment/attributes; on post-create failure it deletes the newly-created group. `NetGroupDel_r` looks up current members, deletes each member from the group, then deletes the group. `NetGroupEnum_r` queries domain group count, calls `QueryDisplayInfo2`, updates the resume handle to the last returned index, and maps display records. `NetGroupSetUsers_r` computes add and delete RID lists by comparing requested users with current membership before applying changes.

## State and Persistence Behavior

The module mutates persistent domain SAM state: group objects, descriptions, attributes, and memberships. It also uses cached SAMR connect/domain handles unless `ctx->disable_policy_handle_cache` requires explicit close. Output state is transient talloc-backed `GROUP_INFO_*` and `GROUP_USERS_INFO_*` buffers attached to `ctx`; resume progress is caller-owned.

## Dependencies and Integration Points

Dependencies include `rpc_client/rpc_client.h`, generated SAMR NDR, LSA string initialization helpers, security SID utilities, `netapi_private` SAMR domain helpers, and user/group buffer helpers such as `add_GROUP_USERS_INFO_X_buffer()` and `add_rid_to_array_unique()`. Public wrappers in `libnetapi.c` dispatch here for non-local servers and local redirects.

## Risks and Edge Cases

The file relies heavily on server response shape checks (`rids.count`, `types.count`, `names.count`) and returns `WERR_BAD_NET_RESP` on mismatch. Some operations validate only `group_name` or `buffer` and rely on downstream SAMR behavior for null user names. `NetGroupGetUsers_r` explicitly notes it does not cope with large replies. Membership operations use hard-coded attribute value `7 /* why ? */`. `NetGroupSetUsers_r` looks up requested names but does not explicitly reject non-user SID types before using returned RIDs. Multi-step membership replacement is not transactional, so partial changes can persist if a later SAMR call fails.

## Test Signals

High-value tests cover all supported info levels 0/1/2/3 and set levels 0/1/2/3/1002/1005, non-group name type rejection, duplicate and missing users, large group member lists, resume-handle group enumeration, create-with-attribute rollback on failure, and behavior with policy-handle caching enabled and disabled.
