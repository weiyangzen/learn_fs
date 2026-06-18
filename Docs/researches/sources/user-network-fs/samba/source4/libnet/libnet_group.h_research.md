# sources/user-network-fs/samba/source4/libnet/libnet_group.h

## Purpose
`libnet_group.h` declares libnet request/result structures for group creation, group information lookup, and group listing.

## Important APIs, Types, And Functions
`struct libnet_CreateGroup` takes group name and domain name, returning `error_string`. `enum libnet_GroupInfo_level` selects lookup by name or SID. `struct libnet_GroupInfo` takes domain name plus either `group_name` or `group_sid`, returning group name, SID, member count, description, and error string. `struct libnet_GroupList` takes domain name, page size, and resume index, returning count, next resume index, and an array of `grouplist { sid, groupname }`.

## Control Flow
The structures correspond to the create/info/list flows in `libnet_group.c`. Group-list callers are expected to handle paged enumeration by feeding `out.resume_index` back into `in.resume_index` when the status indicates more entries.

## State And Persistence Behavior
The header itself is declarative. The create request causes remote SAMR mutation in the implementation; info/list are read-only. Returned pointer fields are allocated under the caller's memory context by the receive wrappers.

## Dependencies And Integration Points
The header references Samba SID types and is consumed by libnet group-management callers and tests. It relies on `libnet/libnet.h` inclusion paths for core types.

## Risks
The union in `libnet_GroupInfo.in.data` must match the selected level. Callers must not assume `GroupList` returns all groups in one call. The group SID output for info-by-SID depends on implementation details and may need validation.

## Test Signals
Compile/API tests should cover both union variants. Functional tests should verify error-string population, paged list semantics, and correct SID/name fields in returned group arrays.
