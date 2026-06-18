# sources/user-network-fs/samba/source3/winbindd/wb_group_members.c

## Purpose
This file implements async recursive group-member expansion. It has three layers: single group lookup, serial lookup over a list of groups, and recursive expansion into unique user/computer members.

## Important APIs, Types, And Functions
Internal APIs are `wb_lookupgroupmem_send/recv` and `wb_groups_members_send/recv`. Public APIs are `wb_group_members_send`, `wb_group_members_recv`, and `add_member_to_db`. Request state structs track current groups, depth, all members, and an RBT database of users.

## Control Flow
Single-group lookup finds the owning domain by SID and calls `dcerpc_wbint_LookupGroupMembers`. List lookup serially walks groups, tolerating `NT_STATUS_TRUSTED_DOMAIN_FAILURE` by treating that group as empty, and appends returned principals. Recursive expansion opens an in-memory RBT db, seeds initial groups, decrements depth per expansion round, looks up all current groups, stores user/computer principals in the db keyed by binary SID, and saves group/alias/well-known principals for the next round. It completes when depth is exhausted or no groups remain.

## State And Persistence
All state is request-local. The member db is an in-memory `dbwrap_rbt` object, not durable. Duplicate users collapse through db key replacement/insert semantics in `add_member_to_db`.

## Dependencies And Integration
It uses generated winbind child RPC stubs, domain lookup, SID NDR sizing/linearization, dbwrap RBT, and tevent. `wb_getgrsid.c` uses it for group member expansion.

## Risks And Test Signals
Test unknown group domain, child RPC failures, trusted-domain failure tolerance, empty groups, nested groups, depth zero, duplicate users, computer members, large expansion, and replacement behavior in the RBT db. Recursion is breadth-like by rounds; cyclic group nesting relies on depth limits and duplicate user db, not a visited-group set.
