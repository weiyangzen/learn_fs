# sources/storage-engines/wiredtiger/test/format/format_salvage.c

Purpose: exercises WiredTiger salvage by first salvaging a valid object, then corrupting a backing file and salvaging again. It is a post-run fault-tolerance path for table/file sources.

Important APIs and functions: `uri_path` maps `table->uri` to an object file path under `g.home`; `corrupt` writes a repeatable corruption marker into a random file span and saves `SALVAGE.corrupt` plus `SALVAGE.copy/<object>.corrupted`; `wts_salvage` drives open, `WT_SESSION::salvage(force=true)`, `table_verify`, and close cycles.

Control flow: `wts_salvage` exits when `GV(OPS_SALVAGE)` is off, creates `SALVAGE.copy`, copies the target object and WiredTiger metadata/log files, opens the database with metadata verification, salvages and verifies, closes, corrupts the object, reopens without metadata verification, salvages again, verifies again, and closes.

State and persistence: it modifies real files in `g.home`, writes diagnostic salvage artifacts, and preserves enough copied state to replay failures. Corruption is roughly 2 percent of file size plus 4 KiB, capped at 1 MiB, and starts at a random offset before the final KiB.

Dependencies and integration: called from `t.c` after normal verification and shutdown, per table via `tables_apply`. It uses `wts_open/wts_close`, `table_verify`, `testutil_copy`, POSIX file APIs, global RNG, and path fields from `GLOBAL`.

Risks and test signals: small files below the assumed offset range would be risky if salvage were enabled for unsuitable objects. The important failures are inability to locate the object, failed salvage, failed verify, or mismatch introduced by salvage. `SALVAGE.corrupt` records the corruption offset/length for reproduction.
