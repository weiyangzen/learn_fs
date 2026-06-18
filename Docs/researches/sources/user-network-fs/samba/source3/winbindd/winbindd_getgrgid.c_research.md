# sources/user-network-fs/samba/source3/winbindd/winbindd_getgrgid.c

## Purpose
Implements async `WINBINDD_GETGRGID`, resolving a Unix GID to a winbind group record with members.

## Important APIs, Types, And Control Flow
The send path builds a single `struct unixid` with `ID_TYPE_GID` and calls `wb_xids2sids_send()`. `winbindd_getgrgid_gid2sid_done()` rejects a null SID, then calls `wb_getgrsid_send()` to obtain domain/name/gid/member db. `winbindd_getgrgid_done()` normalizes the domain/name through `dcerpc_wbint_NormalizeNameMap_send()` on the idmap child. `winbindd_getgrgid_normalize_done()` chooses mapped, renamed, or original full group name. The recv path fills `response->data.gr`, serializes members with `winbindd_print_groupmembers()`, and appends member data to `extra_data`.

## State And Persistence
Reads idmap and group/member data through helper layers. It depends on parent idmap setup already being valid when calling `idmap_child_handle()`.

## Dependencies And Integration Points
Uses idmap xids-to-sids, `wb_getgrsid`, wbint name normalization, `fill_domain_username_talloc()`, and group member printing.

## Risks And Test Signals
The send function logs `request->data.gid` but initializes from `request->data.uid`, which deserves regression coverage against the request union layout. Risks also include null-SID handling, normalization fallbacks, and member serialization. Test mapped/unmapped GIDs, ID_TYPE_BOTH cases, renamed normalized names, empty member lists, and idmap child setup failures.
