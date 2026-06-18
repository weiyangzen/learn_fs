<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/expert/expert.c -->
# sources/storage-engines/sqlite/ext/expert/expert.c

## Purpose
`expert.c` is the standalone command-line frontend for SQLite's expert extension. It opens a database, feeds one or more SQL statements into `sqlite3expert`, runs index analysis, and prints candidate indexes, per-query recommended indexes, and query plans.

## Important APIs, Types, And Functions
`main()` owns the full program lifecycle: argument parsing, database open, expert-handle creation, SQL ingestion, analysis, reporting, and cleanup.

`readSqlFromFile()` reads an entire SQL file into an SQLite-allocated buffer, passes it to `sqlite3_expert_sql()`, and frees the buffer. It reports file-open and short-read failures through `sqlite3_mprintf()` strings owned by the caller.

`usage()`, `option_requires_argument()`, and `option_integer_arg()` are small CLI helpers. Options are matched by prefix using `sqlite3_strnicmp()`, with optional GNU-style `--` reduced to `-` by advancing `zArg` one character. Supported options are `-sql`, `-file`, `-verbose`, and `-sample`.

The SQLite expert API calls used here are `sqlite3_expert_new()`, `sqlite3_expert_sql()`, `sqlite3_expert_config(EXPERT_CONFIG_SAMPLE)`, `sqlite3_expert_analyze()`, `sqlite3_expert_count()`, `sqlite3_expert_report()`, and `sqlite3_expert_destroy()`.

## Control Flow
The final positional argument is treated as the database path. The program rejects missing arguments and a database argument beginning with `-`, opens the database with `sqlite3_open()`, and constructs an expert handle. It then scans all preceding arguments. `-file` consumes the next token and loads SQL from disk, `-sql` consumes the next token as SQL text, `-sample` clamps indirectly through the library config call, and `-verbose` controls how much report text is printed.

After all inputs are loaded, `sqlite3_expert_analyze()` performs the expensive work. On success, verbosity above zero prints the global candidate index list, then each analyzed query is reported. For each query it optionally prints the original SQL, prints recommended `CREATE INDEX` statements or `(no new indexes)`, and prints the post-candidate `EXPLAIN QUERY PLAN` output. On any non-OK return, the program prints the expert error string.

## State And Persistence Behavior
Program state is process-local except for opening and reading the target database and any SQL file. The frontend itself does not create indexes in the user's database; candidate indexes are created inside the expert implementation's in-memory analysis database. The sample percentage controls how much table data the expert library scans to synthesize `sqlite_stat1`.

The error string `zErr` is SQLite-allocated and freed at exit. The expert object and database connection lifetimes are cleanly bounded, although `sqlite3_close(db)` is not called explicitly after `sqlite3_expert_destroy()`.

## Dependencies
The file depends on the SQLite C API, standard C file and memory headers, and `sqlite3expert.h`. It assumes the expert extension was built with virtual table support, because the implementation is compiled out under `SQLITE_OMIT_VIRTUALTABLE`.

## Integration Points
This frontend is the executable wrapper around `ext/expert/sqlite3expert.c`. Build systems can compile it with the SQLite library and expert implementation to provide a `sqlite3_expert`-style utility. Its output format directly reflects `EXPERT_REPORT_CANDIDATES`, `EXPERT_REPORT_INDEXES`, `EXPERT_REPORT_SQL`, and `EXPERT_REPORT_PLAN`.

## Risks And Edge Cases
Option matching is prefix-based, so short prefixes such as `-ver` are accepted and future option names could become ambiguous. `option_integer_arg()` uses `atoi()`, so malformed numeric options silently become zero. `readSqlFromFile()` allocates `nIn+1` bytes based on `ftell()` without validating negative `ftell()` results or allocation failure before `fread()`, which makes unusual file errors or very large files riskier. The CLI does not enforce that at least one SQL statement was supplied; an empty analysis simply reports zero query sections if the library accepts it.

## Test Signals
CLI tests should cover `-sql`, `-file`, single-dash and double-dash spellings, missing option arguments, invalid database paths, sample values below zero and above one hundred, and verbosity zero versus default output. Behavioral tests can compare recommended index output against known queries using the Tcl expert test bindings or the standalone executable.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/expert/expert.c -->
