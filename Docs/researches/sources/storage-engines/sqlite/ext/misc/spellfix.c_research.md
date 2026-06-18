# sources/storage-engines/sqlite/ext/misc/spellfix.c

## Purpose
Implements SQLite's `spellfix1` extension: scalar helper functions for transliteration, phonetic hashing, script detection, fixed-cost edit distance, configurable Unicode edit distance, and a writable `spellfix1` virtual table for fuzzy vocabulary lookup.

## Important APIs, Types, And Functions
The extension registers `spellfix1_translit`, `spellfix1_editdist`, `spellfix1_phonehash`, `spellfix1_scriptcode`, `editdist3`, and module `spellfix1`. Core types include `EditDist3Config`, `EditDist3Lang`, `EditDist3Cost`, `EditDist3FromString`, `spellfix1_vtab`, `spellfix1_cursor`, and `MatchQuery`. Important functions are `phoneticHash`, `editdist1`, `editDist3ConfigLoad`, `editDist3Core`, `transliterate`, `scriptCodeSqlFunc`, `spellfix1Init`, `spellfix1BestIndex`, `spellfix1FilterForMatch`, `spellfix1RunQuery`, `spellfix1FilterForFullScan`, `spellfix1Column`, `spellfix1Update`, and `spellfix1Register`.

## Control Flow
On load, `sqlite3_spellfix_init()` calls `spellfix1Register()`. `xCreate` creates a shadow table named `<vtab>_vocab` with `id`, `rank`, `langid`, `word`, `k1`, and `k2`, plus an index on `(langid,k2)`. `xBestIndex` recognizes `word MATCH`, optional `langid`, `top`, `scope`, distance bounds, and rowid equality. MATCH scans transliterate the query, optionally precompile the Unicode edit-distance source, build a phonetic-hash range, scan the shadow table by `langid` and `k2`, compute edit distance, keep the best ranked rows, then sort by score. Full scans and rowid lookups prepare direct shadow-table SELECTs.

## State And Persistence Behavior
Persistent state is in the shadow vocabulary table and its index. Inserts and updates compute `k1` from a transliterated word or `soundslike`, lower-case it, compute `k2` with `phoneticHash`, and write shadow rows. Deletes remove by `id`. `command='reset'` clears cached edit costs, and `command='edit_cost_table=...'` changes the cost table reference. Virtual-table instances cache database/table names and loaded edit-cost configuration; cursors own result arrays, prepared statements, and pattern strings.

## Dependencies And Integration Points
Depends on SQLite extension, virtual table, scalar function, memory, statement, and SQL formatting APIs. It integrates with SQLite's virtual-table planner, shadow-table storage, `sqlite3_vtab_on_conflict()`, `sqlite3_declare_vtab()`, `sqlite3_create_module()`, and application-provided edit-cost tables.

## Risks And Edge Cases
`editdist1` only accepts ASCII and rejects very large inputs; `editdist3` caps input sizes and treats costs >=10000 as infinite. Transliteration uses a fixed sorted table and maps unknown non-ASCII to `?`. MATCH quality depends heavily on the phonetic hash prefix scope and shadow-table `k2` index. Shadow SQL is dynamically generated but uses `%w`/`%Q` quoting for identifiers and values. Cursor result resizing can drop accumulated rows on allocation failure. `xUpdate` allows control commands through hidden columns, so tests should cover invalid commands and cost-table reloads.

## Test Signals
Useful tests include scalar transliteration/phonehash/edit-distance fixtures, `editdist3` custom cost tables, script-code cases for Latin/Cyrillic/Greek/Hebrew/Arabic/mixed/none, virtual-table insert/update/delete/rename/drop behavior, MATCH with `top`, `scope`, `langid`, distance bounds, prefix `*`, rowid lookup, conflict modes, and OOM/error propagation from shadow SQL.
