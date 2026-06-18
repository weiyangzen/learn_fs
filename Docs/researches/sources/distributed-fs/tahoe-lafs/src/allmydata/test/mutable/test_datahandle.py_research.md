<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_datahandle.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_datahandle.py

Purpose: Tests `MutableData`, the in-memory mutable uploadable wrapper.

Important APIs and functions: `DataHandle.setUp` creates repeated byte test data and wraps it in `MutableData`. Tests cover `read(chunk_size)` and `get_size()`.

Control flow: Read tests repeatedly call `read(10)` and compare joined chunks to sequential slices. Size tests assert the declared size equals the original bytes and that `get_size` does not disturb the read cursor.

State and persistence: State is the `MutableData` object's in-memory cursor and byte buffer. No files or storage servers are touched.

Dependencies and integration points: Uses `SyncTestCase`, `MutableData`, and `testtools` matchers `Equals`/`HasLength`. This validates uploadable behavior consumed by mutable publisher tests.

Risks: The test assumes `read` returns an iterable of byte chunks rather than a single bytes object. Cursor preservation around `get_size` is the main contract.

Test signals: Sequential reads must be ordered and complete; `get_size` must be idempotent and non-seeking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_datahandle.py -->
