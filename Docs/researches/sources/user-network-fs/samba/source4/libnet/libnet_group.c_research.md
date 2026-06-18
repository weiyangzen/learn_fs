# sources/user-network-fs/samba/source4/libnet/libnet_group.c

## Purpose
`libnet_group.c` implements source4 libnet operations for creating groups, retrieving group information, and listing domain groups over SAMR/LSA RPC. It follows the library's composite async pattern with synchronous wrappers.

## Important APIs, Types, And Functions
Public APIs are `libnet_CreateGroup_send/recv()` and `libnet_CreateGroup()`, `libnet_GroupInfo_send/recv()` and `libnet_GroupInfo()`, and `libnet_GroupList_send/recv()` and `libnet_GroupList()`.

`create_group_state` tracks the domain-open prerequisite and `libnet_rpc_groupadd` call. `group_info_state` supports lookup-by-name or lookup-by-SID, carrying `libnet_LookupName` and `libnet_rpc_groupinfo` requests. `grouplist_state` carries LSA domain info, SAMR group enumeration state, resume index, page size, and returned group array.

## Control Flow
Group creation first ensures a SAMR domain handle through `samr_domain_opened()`. If the prerequisite is already met it immediately sends `libnet_rpc_groupadd_send()`, otherwise it resumes from `continue_domain_opened()` after `libnet_DomainOpen_recv()`. Completion is just `libnet_rpc_groupadd_recv()` followed by `composite_done()`.

Group info first opens the SAMR domain. For `GROUP_INFO_BY_NAME`, it resolves the name through `libnet_LookupName_send()`, verifies the SID type is a domain group or alias, and then requests full group info by SID/name. For `GROUP_INFO_BY_SID`, it converts the provided SID to a string and calls groupinfo directly. Results copy group name, SID, member count, and description into the caller output.

Group list first ensures an LSA policy handle, queries `LSA_POLICY_INFO_DOMAIN` to obtain the domain SID, ensures a SAMR domain handle, then sends `samr_EnumDomainGroups`. It accepts OK, `STATUS_MORE_ENTRIES`, and `NT_STATUS_NO_MORE_ENTRIES` as successful enumeration states, builds SIDs by adding each returned RID to the queried domain SID, and returns resume index/count/groups.

## State And Persistence Behavior
Create group persists a new group account on the remote domain through SAMR. Info and list are read-only. The functions rely on and may populate cached SAMR/LSA domain handles in `libnet_context` through prerequisite helpers. Returned arrays and strings are talloc-moved to the caller memory context.

## Dependencies And Integration Points
Dependencies include `libnet_DomainOpen`, `libnet_LookupName`, SAMR/LSA generated RPC calls, `libnet_rpc_groupadd`, `libnet_rpc_groupinfo`, security SID helpers, and monitor callbacks. This file is structurally parallel to source4 user-management helpers.

## Risks
Group list returns only the current SAMR enumeration page; callers must use `resume_index` to continue on `STATUS_MORE_ENTRIES`. `libnet_GroupInfo_recv()` steals `s->lookup.out.sid` even for lookup-by-SID mode, where the lookup path is not populated, so SID output may be null despite successful info by SID. SID type filtering for lookup-by-name rejects non-group names but relies on LSA lookup returning accurate type. Remote mutation in create has no rollback if later receive/error handling fails.

## Test Signals
Tests should cover successful group creation, prerequisite domain-open paths both already-open and async-open, group info by name for domain groups and aliases, rejection of users/computers as `NT_STATUS_NO_SUCH_GROUP`, info by SID output fields, paged group listing with resume index, and all three accepted enumeration statuses.
