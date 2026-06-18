# sources/storage-engines/wiredtiger/examples/c/ex_schema.c

Purpose: demonstrates schema features: named columns, column groups, simple/composite/immutable indexes, raw cursors, and projected access.

Important APIs and control flow: defines `POP_RECORD` sample data. `main` creates `table:poptable` with record-number keys, value format `5sHQ`, named columns, and `main`/`population` column groups. It creates simple `country`, composite `country_plus_year`, and immutable `year` indexes. It appends sample rows, scans and updates populations, lists rows normally and in raw mode via `wiredtiger_struct_unpack`, reads through both column groups, searches simple and composite indexes, and closes.

State and persistence: persists population rows, column-group storage, and indexes. Updates increment every population after insertion, so later reads observe modified state.

Dependencies and integration: uses format-string packing semantics, index projection syntax, and `test_util.h`.

Risks: fixed-width country strings require padded search keys such as `"AU\0\0\0"` and `"USA\0\0"`. Immutable index correctness depends on not updating indexed `year` values.

Test signals: normal/raw scans must agree, column group lookups for record 2 must return expected fields, and simple/composite index searches must succeed.
