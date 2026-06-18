# sources/user-network-fs/samba/source3/winbindd/winbindd_getgrnam.c

## Purpose
Implements async `WINBINDD_GETGRNAM`, resolving a group name to a POSIX group structure and member list.

## Important APIs, Types, And Control Flow
`winbindd_getgrnam_send()` copies and null-terminates the requested group, then runs `wb_parent_idmap_setup_send()` before talking to the idmap child. The initialized callback calls `NormalizeNameUnmap`; the unmap callback parses namespace/domain/group with `parse_domain_user()`, defaults empty/local domains to `get_global_sam_name()`, and calls `wb_lookupname_send()`. `lookupname_done()` accepts group, alias, well-known group, user, and computer SID types to allow ID_TYPE_BOTH-backed group records, then calls `wb_getgrsid_send()`. After `NormalizeNameMap`, recv fills `struct winbindd_gr` and serializes members.

## State And Persistence
Maintains only request-local strings, SID, gid, and member db. Parent idmap setup can initialize the global idmap child/config cache.

## Dependencies And Integration Points
Uses parent idmap setup, wbint normalization on the idmap child, name parsing, `wb_lookupname`, `wb_getgrsid`, `lp_winbind_expand_groups()`, and `winbindd_print_groupmembers()`.

## Risks And Test Signals
Risks include name mapping/unmapping mismatches, default-domain behavior for local aliases, accepting user/computer SID types, and output name formatting differences when normalization returns `NT_STATUS_FILE_RENAMED`. Test domain-qualified and unqualified names, local SAM aliases, normalized names, users mapped as both, unsupported SID types, and huge member lists.
