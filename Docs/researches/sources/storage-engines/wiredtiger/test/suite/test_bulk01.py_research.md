# sources/storage-engines/wiredtiger/test/suite/test_bulk01.py

Purpose: broad smoke and contract test for bulk-load cursors across file/table URIs, integer/record-number/string keys, and integer/string values.

Important APIs/types/functions: `simple_key`, `simple_value`, `make_scenarios`, `stat.conn.cursor_bulk_count`, `session.open_cursor(..., "bulk")`, bulk `append`, `skip_sort_check`, and error assertions.

Control flow: scenario matrix creates objects and tests normal bulk insert/stat increments, variable-length column-store RLE-friendly repeated values, append mode ignoring supplied keys, skipped record handling in column store, very large record numbers, order checking failures for nonmonotonic keys, bulk open rejection on nonempty objects, and busy rejection while another cursor is open. One row-order skip-sort diagnostic test is currently skipped.

State/persistence behavior: bulk cursors populate newly created btrees and must close into normal readable state. Column-store gaps must persist as missing records, and append allocation must assign sequential record numbers.

Dependencies/integration: cursor statistics, btree bulk load path, row/column formats, diagnostic behavior, checkpoint before nonempty rejection, and public error messages.

Risks/test signals: combines many small scenarios; errors include wrong stat counts, incorrect values after append/gaps, missing order-check errors, or allowing illegal bulk cursors.
