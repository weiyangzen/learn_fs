# sources/storage-engines/sqlite/test/optfuzz-db01.c

## Purpose

`optfuzz-db01.c` embeds `testdb01.db` as `unsigned char data001[]`. It is the fixed read-only SQLite database fixture used by `optfuzz.c` to compare optimized and non-optimized query results without relying on an external database file.

## Important APIs, Types, and Data

The only top-level symbol is `data001`. The byte stream is a valid SQLite database image containing optimizer-sensitive schema and data: rowid and WITHOUT ROWID tables, primary keys, unique constraints, autoindexes, explicit indexes, numeric/text data, aggregate views, compound-query views, joins, left joins, ORDER BY/LIMIT views, and recursive CTE coverage.

## Control Flow

There is no executable logic. `optfuzz.c` includes this file and calls `sqlite3_deserialize(dbRun, "main", data001, sizeof(data001), sizeof(data001), SQLITE_DESERIALIZE_READONLY)`.

## State and Persistence Behavior

The array is static program data and is treated as a read-only in-memory database image. It creates no files and stores no runtime state by itself.

## Dependencies and Integration Points

It is tightly coupled to `optfuzz.c` and SQLite’s deserialize API. The fixture is the schema/data oracle for optimizer fuzzing and must remain valid as a database byte image.

## Risks and Test Signals

Manual edits are unsafe because a single byte can corrupt the database. The non-`static` global symbol can conflict if included into multiple translation units. Signals are indirect: successful deserialization and meaningful optimizer/no-optimizer comparison runs in `optfuzz.c`.
