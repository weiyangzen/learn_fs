# sources/sync-backup/casync/test/test-caindex.c

Purpose: test utility for reading and dumping casync index entries.

Important APIs/types/functions: opens a `CaIndex` from argv path, repeatedly reads entries/locations, and prints or validates each result.

Control flow/state: creates a read-mode index object, sets path, opens it, loops until EOF, then exits. State is in the index reader.

Dependencies/integration: used manually or by scripts to inspect `.caidx` behavior. Depends on `caindex` and origin/location code.

Risks/test signals: requires an input index file, so it is less self-contained than unit tests. It is useful for detecting parser failures on generated indexes.

Source research group: `subset-b-009122`.
