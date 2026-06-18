# File Research: sources/local-fs/xfsprogs/db/addr.c

Implements the `addr` / `a` command, which evaluates a field expression against the current typed buffer and moves the `xfs_db` cursor to the address represented by the selected field. With no argument it prints the current cursor. With an expression it scans/parses field paths via `flist_scan` and `flist_parse`, rejects array ranges, resolves the destination type from the terminal field’s `next` type, and invokes that field type’s address function (`ftattrtab[fld->ftyp].adfunc`).

Integration is through `addr_init`, which registers the command. The command depends on the field/type/faddr/flist machinery and on `inode_next_type` for dynamic inode-data destinations. It is intentionally non-mutating; primary failure paths are invalid current type, fields without address functions, array selections, or fields without next-type metadata.
