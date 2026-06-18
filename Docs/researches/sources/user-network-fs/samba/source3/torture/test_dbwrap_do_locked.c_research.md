# sources/user-network-fs/samba/source3/torture/test_dbwrap_do_locked.c

Purpose: This file tests `dbwrap_do_locked()` against a watched dbwrap database. It verifies that a callback can atomically store a record while holding the lock, that the stored value is visible through parsing, and that a second locked callback can delete the record.

Important APIs/types/functions: `struct do_locked1_state` carries the expected value and callback status. `do_locked1_cb()` stores through `dbwrap_record_store()`, `do_locked1_check()` compares using `tdb_data_cmp()`, and `do_locked1_del()` deletes via `dbwrap_record_delete()`. `run_dbwrap_do_locked1()` opens a TDB backend, wraps it with `db_open_watched()`, and exercises `dbwrap_do_locked()` and `dbwrap_parse_record()`.

Control flow: The public test initializes global event and messaging contexts, opens `test_do_locked.tdb` with `TDB_CLEAR_IF_FIRST`, wraps the backend, stores `"value"` under key `"key"` through a locked callback, parses the record to verify bytes, deletes through another locked callback, then parses again expecting `NT_STATUS_NOT_FOUND`.

State/persistence behavior: The test creates a local TDB file and removes it at the end with `unlink(dbname)`. Record state is transient and intentionally moves through absent -> present -> absent. The watched wrapper also maintains watcher metadata internally, although this test focuses on lock callback behavior.

Dependencies and integration points: It depends on `lib/dbwrap`, watched dbwrap support, util TDB helpers, source3 util TDB helpers, and global Samba event/messaging contexts. It integrates with the same watched dbwrap layer used by higher-level database notification code.

Risks: Cleanup only unlinks on the normal fail label after `db` is created; early backend-open failures can leave nothing to clean but also skip `backend` free. Failures in watched backend behavior may surface as callback status mismatches rather than direct `dbwrap_do_locked()` errors.

Test signals: Passing requires `dbwrap_do_locked()` to return OK for store and delete, callback status to be OK, parse comparison to match exactly, and final parse to return `NT_STATUS_NOT_FOUND`.
