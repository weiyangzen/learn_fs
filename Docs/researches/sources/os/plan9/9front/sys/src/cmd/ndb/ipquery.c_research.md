# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/ipquery.c

Small wrapper around `ndbipinfo`.

Key elements:
- Usage: `ipquery attr value rattribute`.
- Supports `-f` to choose an ndb file.
- Opens the database, calls `ndbipinfo(db, attr, val, rattr, nrattr)`, and prints returned tuples as `attr=value`.
- Installs `$` formatter via `ndbvalfmt`.

Notable behavior:
- Prints all tuple entries in the returned linked entry list on one line.

Risks and quirks:
- Minimal validation beyond argument count and database open failure.
