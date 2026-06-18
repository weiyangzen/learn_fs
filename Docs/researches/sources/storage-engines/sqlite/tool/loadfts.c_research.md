# sources/storage-engines/sqlite/tool/loadfts.c

## Purpose
`loadfts.c` is a command-line performance-test helper that creates an SQLite FTS3, FTS4, or FTS5 table and recursively loads file contents from a directory tree into a single-column `fts` virtual table. It can also issue special FTS control inserts and optionally batch inserts in transactions.

## Important APIs, Types, and Functions
- `readfileFunc()` implements SQL function `readtext(X)`, reading an entire path into SQLite-allocated memory and returning it as UTF-8 text.
- `showHelp()`, `error_out()`, and `sqlite_error_out()` provide CLI usage and fatal diagnostics.
- `struct VisitContext` carries `nRowPerTrans`, `sqlite3 *db`, and prepared insert statement `pInsert`.
- `visit_file()` binds a file path into `INSERT INTO fts VALUES(readtext(?))`, steps/resets the statement, and commits/begins every configured row interval.
- `traverse()` recursively walks directories with `opendir()`, `readdir()`, `dirent.d_type`, and `sqlite3_mprintf()` path construction.
- `main()` parses switches, opens the database, creates the scalar SQL function, creates the FTS virtual table, applies `-special` commands, prepares insert SQL, traverses files, finalizes, closes, and frees.

## Control Flow
1. The program expects switch/value pairs followed by the database path; malformed arity or unknown options call `showHelp()`.
2. CLI options select FTS version (`-fts 3|4|5`), mapping-table flag (`-idx 0|1` parsed but not used elsewhere), root directory (`-dir`), transaction interval (`-trans`), and repeated `-special` commands.
3. `sqlite3_open()` opens the target DB and `sqlite3_create_function()` registers `readtext`.
4. It creates `CREATE VIRTUAL TABLE fts USING fts%d(content)`, then executes each special command as `INSERT INTO fts(fts) VALUES(%Q)`.
5. It prepares the insert statement, starts a transaction if requested, recursively traverses the input directory, inserts every non-directory entry, commits periodically based on last rowid, commits at the end, and cleans up.

## State and Persistence Behavior
- Persistent state is the target SQLite database. The program creates and populates a virtual table named `fts`; rerunning against a database that already has that table will fail at creation.
- `readfileFunc()` loads one complete file into memory per SQL call and transfers ownership to SQLite with `sqlite3_free` as destructor on success.
- Transaction behavior is controlled by `nRowPerTrans`; a positive value wraps inserts in `BEGIN`/`COMMIT` and commits every rowid multiple.
- Directory traversal is depth-first recursion and does not persist a file manifest.

## Dependencies and Integration Points
- Depends on SQLite public C API and FTS modules compiled/loaded into the SQLite library.
- Depends on POSIX directory APIs (`dirent.h`, `opendir`, `readdir`, `closedir`) and `dirent.d_type`.
- Integrates with SQLite's FTS control channel through `INSERT INTO fts(fts) VALUES(...)` for `-special`.
- Intended for benchmark/test workloads rather than general-purpose ingestion.

## Risks and Edge Cases
- `-idx` is parsed and validated but never used; users may expect a filename-to-rowid mapping table that this version does not create.
- `readfileFunc()` uses `ftell()` into `long` and `sqlite3_malloc(nIn)` without explicit negative/large-size checks; very large files can fail or stress memory.
- A zero-length file causes `sqlite3_malloc(0)` and `fread(..., 0, 1, ...)`, which may not return the success condition, yielding NULL/no result rather than empty text.
- Traversal relies on `d_type & DT_DIR`; filesystems that return `DT_UNKNOWN` will treat directories as files and skip recursion.
- No filtering is applied for binary files, symlinks, hidden files, or unreadable files; unreadable files become NULL text silently through `readtext`.
- Periodic commit uses `sqlite3_last_insert_rowid() % nRowPerTrans`, which assumes rowids advance with each insert into the FTS table as expected.

## Test Signals
- Build against SQLite with FTS3/4/5 enabled and run with `-fts 3`, `-fts 4`, and `-fts 5`.
- Load a small directory tree and verify `SELECT count(*) FROM fts`.
- Test nested directories, empty files, unreadable files, large files, binary files, and filesystems with unknown `d_type`.
- Test `-trans` boundaries and `-special` commands such as FTS optimize/merge operations supported by the selected FTS version.
- Confirm current `-idx` behavior before relying on any mapping table.
