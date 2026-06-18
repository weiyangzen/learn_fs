# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ldb/ListTables.java

Purpose: `ListTables` lists RocksDB column families for the parent ldb database path.

Important APIs and types: It implements `Callable<Void>`, uses parent `RDBParser`, `RocksDatabase.listColumnFamiliesEmptyOptions`, and UTF-8 decoding.

Control flow: `call()` obtains the DB path from the parent, lists column family byte names, converts each to a UTF-8 string, and prints one per line.

State and persistence behavior: It reads RocksDB metadata only and writes to stdout.

Dependencies and integration points: It is an ldb subcommand useful before `scan` or `value-schema`.

Risks: It assumes column family names are UTF-8, which matches Ozone table names.

Test signals: Printed column family list for a valid DB path.
