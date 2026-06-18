# sources/user-network-fs/nfs-utils/support/reexport/backend_sqlite.c

Purpose: `backend_sqlite.c` implements the sqlite-backed reexport database that maps export paths to stable numeric fsid values.

Important APIs and control flow: `sqlite_plug_init` seeds a small PRNG for lock backoff, opens the configured database, and creates `fsidnums(num INTEGER PRIMARY KEY, path TEXT UNIQUE)`. `get_fsidnum_by_path` and `sqlite_plug_path_by_fsidnum` run prepared SELECTs. `new_fsidnum_by_path` inserts the smallest free positive fsid via an SQL self-join/UNION query with `RETURNING`, handling unique races by rechecking. `sqlite_plug_fsidnum_by_path` combines lookup and optional creation.

State, dependencies, and integration: Static `sqlite3 *db` and `init_done` hold plugin state. The backend is exported as `sqlite_plug_ops` for `fsidd`.

Risks and test signals: `sqlite_plug_destroy` closes the DB but does not reset `init_done`, `new_fsidnum_by_path` may not mark success after the constraint recheck, and backoff is randomized but unbounded by total time. Tests should cover concurrent creation races, locked DBs, path uniqueness, fsid reuse gaps, database config override, and init/destroy/reinit.
