# sources/user-network-fs/samba/source3/winbindd/wb_getgrsid.c

## Purpose
This async helper builds a `getgr*`-style group result from a group SID: it resolves the SID name/type, maps it to a GID, and expands group or alias members into an in-memory db.

## Important APIs, Types, And Functions
`struct wb_getgrsid_state` stores SID, nesting, resolved domain/name/type, GID, member db, and intermediate SID arrays. Public APIs are `wb_getgrsid_send` and `wb_getgrsid_recv`. Callback chain includes lookup SID, SID-to-GID, group member expansion, alias member expansion, alias member name lookup, and nested group merge.

## Control Flow
The send function rejects unmapped Unix group SIDs, then calls `wb_lookupsid_send`. The lookup callback accepts domain groups, aliases, well-known groups, and user/computer SIDs that may map to `ID_TYPE_BOTH`, then calls `wb_sids2xids_send`. The GID callback requires GID or BOTH. User/computer with BOTH is represented as a synthetic group containing only itself. Aliases call `wb_alias_members_send`, then `wb_lookupsids_send` to classify direct members; user/computer direct members are added to an RBT db and domain groups are expanded with `wb_group_members_send`. Domain groups call `wb_group_members_send` directly. Well-known groups produce an empty member db.

## State And Persistence
State is request-local. Members are collected in a `dbwrap_rbt` in-memory database keyed by linearized SID, with string names as values. No durable state is written.

## Dependencies And Integration
It depends on `wb_lookupsid`, `wb_sids2xids`, `wb_alias_members`, `wb_lookupsids`, `wb_group_members`, idmap child setup elsewhere, SID helpers, and dbwrap RBT. It is used by winbind group enumeration and getgrgid/getgrnam flows.

## Risks And Test Signals
Test Unix group SID rejection, SID types, ID_TYPE_BOTH synthetic user group handling, alias direct users, alias nested groups, depth decrement behavior, merge of direct alias members with nested group members, well-known empty groups, and child RPC failures. The alias path builds temporary arrays on `talloc_tos`; ownership and cleanup should be watched under nested expansion.
