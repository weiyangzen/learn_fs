# sources/user-network-fs/samba/source3/winbindd/wb_lookupsid.c

## Purpose
This async helper resolves a SID to domain name, account name, and LSA SID type through the appropriate winbind child domain.

## Important APIs, Types, And Functions
`struct wb_lookupsid_state` stores event context, target SID, result type, domain name, and name. Public APIs are `wb_lookupsid_send` and `wb_lookupsid_recv`.

## Control Flow
The send function copies the SID, finds the lookup domain by SID, and sends `dcerpc_wbint_LookupSid` to that child. The callback handles transport/result status. The recv function moves domain/name strings to the caller and returns the SID type.

## State And Persistence
State is request-local. The child may consult caches or domain controllers; this file does not persist data.

## Dependencies And Integration
It depends on SID-to-domain lookup, child binding handles, generated winbind RPC stubs, tevent, and debug logging. It is a building block for passwd/group and idmap flows.

## Risks And Test Signals
Test unknown SID domain, child RPC failures, name/domain ownership transfer, builtin/well-known SIDs, and result type propagation. Callers often branch heavily on SID type, so fixture coverage should include users, computers, domain groups, aliases, and well-known groups.
