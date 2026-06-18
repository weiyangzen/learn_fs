<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_filehandle.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_filehandle.py

Purpose: Tests `MutableFileHandle`, the file-like-object uploadable wrapper for mutable publishes.

Important APIs and functions: `FileHandle.setUp` wraps a `BytesIO` in `MutableFileHandle`. Tests cover sequential `read`, `get_size`, cursor preservation, operation against a real file object, and `close`.

Control flow: Reads walk the test data in 10-byte chunks; size tests call `get_size` between reads to ensure the handle seek position is restored. The real-file test writes bytes to a temporary file, opens it, wraps it, reads all content, and checks size. `test_close` closes the uploadable and asserts the underlying handle closed.

State and persistence: Uses in-memory `BytesIO` and one temporary directory/file under `mktemp`. No Tahoe storage state.

Dependencies and integration points: Depends on `SyncTestCase`, Python `BytesIO`, filesystem APIs, and `MutableFileHandle`. This behavior feeds mutable publisher upload paths that accept file handles.

Risks: The test opens a real file without a context manager and relies on process cleanup. Cursor preservation is essential; an implementation that seeks to compute size but does not restore would corrupt uploads.

Test signals: Sequential data equality, accurate size, no cursor movement from `get_size`, compatibility with real file objects, and underlying handle closure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_filehandle.py -->
