# File Research: sources/local-fs/xfsprogs/db/flist.h

Purpose: public types and declarations for field-list parsing.

Key contents:
- Defines `flist_t`, a tree/sibling representation of selected fields with array range, flags, and computed offset.
- Defines `FL_OKLOW` and `FL_OKHIGH` array-index validity flags.
- Defines token enum `tokty_t` and token structure `ftok_t`.
- Declares allocation/free, parse, debug print, scan, and field-type search functions.

Interactions:
- Used by `crc.c`, print code, and field traversal users.

Risks/notes:
- Exposes internal parser data structures directly to callers.
