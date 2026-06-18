# sources/user-network-fs/samba/source3/winbindd/winbindd_group.c

## Purpose
Provides shared serialization of group-member databases into the comma-separated member string used by winbind group responses.

## Important APIs, Types, And Control Flow
`winbindd_print_groupmembers()` traverses a `db_context` twice. `getgr_calc_memberlen()` counts records and sums stored value sizes while detecting overflow by checking wrapped length. It then allocates a buffer of the summed size. `getgr_unparse_members()` copies each stored value except its trailing NUL, appends a comma, and advances an offset. After traversal, the final comma is replaced by NUL when the computed length is nonzero. It returns the member count and allocated result buffer.

## State And Persistence
Reads a transient dbwrap database of member names. Does not modify the database or persist output beyond caller-owned talloc memory.

## Dependencies And Integration Points
Used by `GETGRENT`, `GETGRGID`, and `GETGRNAM` response paths. Depends on dbwrap traversal/value APIs and talloc allocation.

## Risks And Test Signals
If there are zero members, it allocates a zero-length buffer and does not explicitly store a NUL; consumers must tolerate that. Risks also include malformed record values without trailing NUL and overflow handling that returns traversal success. Test empty groups, one member, many members, long names, non-NUL values, traversal failure, and allocation failure.
