# sources/storage-engines/wiredtiger/test/suite/test_empty.py

Purpose: ensures newly created empty file/table objects do not write blocks beyond the initial allocation sector.

Important APIs and control flow: scenarios cover file/table with recno and string key formats. `test_empty_create` creates the object, closes the session, maps table URI to its `.wt` filename when needed, and checks filesystem size.

State and persistence: the file should exist with size exactly `4 * 1024`. No records are inserted and no explicit checkpoint is needed beyond create/close behavior.

Dependencies and integration: uses `os.stat`, `make_scenarios`, `wttest.skip_for_hook("tiered")`, and column-store related key formats.

Risks and test signals: direct filename inspection is incompatible with tiered storage. A larger file size indicates empty-object creation wrote unexpected pages or metadata blocks.
