# sources/storage-engines/wiredtiger/test/suite/test_bug009.py

Purpose: regression test for reconciliation page splitting with prefix-compressed string keys. The test creates a file object with `prefix_compression=1`, 4KB internal/leaf pages, `leaf_value_max=3096`, and string key/value formats, then inserts two similarly prefixed keys with large values sized around the split boundary.

Important APIs/types/functions: `wttest.WiredTigerTestCase`, `session.create`, `session.open_cursor`, cursor item assignment, and the file URI `file:test_bug009`. There are no helper methods; all behavior is in `test_reconciliation_prefix_compression`.

Control flow: create the object, open one cursor, insert `fill_2__b_27` and `fill_2__b_28`. The absence of an exception is the test signal.

State/persistence behavior: the inserted records force reconciliation to account for prefix compression when deciding how much material fits on a page. The risk under test is overestimating on-page size and choosing an invalid split.

Dependencies/integration: exercises btree reconciliation, prefix compression, page-size limits, and large value handling through the public Python API.

Risks/test signals: the test is narrow and has no explicit readback; its value is detecting assertions, write failures, or crashes during insert/reconciliation pressure.
