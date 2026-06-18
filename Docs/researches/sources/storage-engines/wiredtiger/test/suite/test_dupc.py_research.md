# sources/storage-engines/wiredtiger/test/suite/test_dupc.py

Purpose: tests cursor duplication through `session.open_cursor(None, cursor, None)`.

Important APIs and control flow: scenarios cover file/table and recno/string key formats. `iterate` walks the dataset with a cursor; at each positioned row it duplicates the cursor, compares original and duplicate with `cursor.compare(dupc)`, verifies the duplicate key, closes the original, and continues iteration using the duplicate.

State and persistence: datasets are fully populated before iteration. The test then drops the object before running a complex table scenario.

Dependencies and integration: uses `SimpleDataSet`, `ComplexDataSet`, `make_scenarios`, `wiredtiger.WT_NOTFOUND`, and `dropUntilSuccess`.

Risks and test signals: exact key equality, compare result zero, full row count, and final `WT_NOTFOUND` validate duplicate cursor positioning and lifetime. Tiered storage is skipped because the complex column-store sequence is not compatible there.
