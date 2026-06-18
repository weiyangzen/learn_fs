# sources/storage-engines/sqlite/ext/misc/amatch.c

## Purpose
`amatch.c` implements the `approximate_match` SQLite virtual table module, a demonstration approximate string matcher. It searches a configured vocabulary table for strings near an input string according to edit-cost rules stored in a separate table.

## Important APIs, types, and functions
- Virtual table structs: `amatch_vtab` stores configuration, rules, generic insertion/deletion/substitution costs, a cached vocabulary-check statement, active cursor count, and the database handle; `amatch_cursor` stores search state, cost limit, language id, input, current output, and AVL queues.
- Rule/search structs: `amatch_rule`, `amatch_word`, and `amatch_avl`.
- AVL helpers maintain priority and duplicate-detection trees: search, insert, remove, rotations, and balancing.
- Rule loading functions parse and validate the edit-distance table: `amatchLoadOneRule()`, `amatchLoadRules()`, `amatchMergeRules()`, and `amatchFreeRules()`.
- Virtual table methods: `amatchConnect()`, `amatchDisconnect()`, `amatchOpen()`, `amatchClose()`, `amatchFilter()`, `amatchNext()`, `amatchColumn()`, `amatchRowid()`, `amatchEof()`, `amatchBestIndex()`, `amatchUpdate()`.
- Entry point `sqlite3_amatch_init()` registers module name `approximate_match`.

## Control flow
Creation parses arguments such as `vocabulary_table`, `vocabulary_word`, `vocabulary_language`, and `edit_distances`, dequotes identifiers, loads edit rules, records generic rules, declares columns `word`, `distance`, `language`, `command HIDDEN`, and `nword HIDDEN`, and marks the virtual table innocuous.

Query planning recognizes `word MATCH ?`, `distance <|<= ?`, and `language = ?` constraints as a bitmask. Filtering initializes the cursor with an input string, max distance, language id, and seed empty word. `amatchNext()` repeatedly removes the lowest-cost partial word from the cost AVL tree, checks whether it is a vocabulary match, and expands candidates by direct next-codepoint match, generic insert/substitute/delete costs, and configured language-specific transformation rules. Duplicate partial states are keyed by matched input length plus output word; lower-cost duplicates update the priority queue instead of adding another node.

## State and persistence behavior
The extension does not persist its own data. It reads persistent vocabulary and rule tables from the database. Rule data is cached in memory for the lifetime of the virtual table. Cursor state is in-memory only and can grow exponentially with distance bounds. A cached `pVCheck` statement on the vtab is prepared lazily and reused across cursor advances.

## Dependencies and integration points
The file depends on SQLite virtual table APIs, extension initialization, SQL preparation/stepping, memory allocation, and host vocabulary/rule tables. Efficient operation depends on an index on the vocabulary word column. It is omitted when `SQLITE_OMIT_VIRTUALTABLE` is defined.

## Risks and edge cases
- Runtime and memory use are exponential in the distance bound; the documentation explicitly recommends tight limits.
- `amatchNext()` mutates `zNext[i-1]++` with a `FIX ME` comment, indicating rough prefix enumeration.
- Generic rule costs use `rIns`, `rDel`, and `rSub`; unset values disable those expansions.
- The cached `pVCheck` statement lives on the vtab while cursors can be active, so cursor concurrency depends on SQLite virtual table scheduling assumptions.
- The module is demonstration-quality and read-mostly; `xUpdate` rejects deletes/updates and allows only no-op command-column inserts.

## Test signals
The file comments describe SQL usage and constraints but no formal in-tree tests are referenced here. Practical test signals are creation with valid/invalid config, matching with language and distance constraints, ordering by distance, rejection of writes, and stress tests for bounded distance growth.
