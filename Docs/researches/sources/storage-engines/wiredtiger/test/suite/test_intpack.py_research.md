# sources/storage-engines/wiredtiger/test/suite/test_intpack.py

Purpose: validates WiredTiger integer packing across all signed and unsigned integer format codes by writing values as keys and values and checking secondary indexes.

Important APIs and functions: `PackTester` manages four cursors/tables per format: forward table (`int key -> packed value`), reverse table (`packed key -> int value`), and inverse indexes. Methods `initialize`, `truncate`, `closeall`, and `check_range` encapsulate setup and validation. `test_intpack` scenarios cover `b/B/h/H/i/I/l/L/q/Q`.

Control flow: for each format, the test asserts the valid range size equals `2 ** nbits`, initializes tables/indexes, checks a base range around zero, checks ranges around `2**32` for 32-bit-or-larger formats, and checks ranges near powers of two up to `1 << 60` for 64-bit formats after truncation.

State and persistence behavior: data is stored in table keys, table values, and secondary indexes to exercise both pack and unpack directions. Persistence is not checkpoint-focused; correctness is immediate cursor/index retrieval.

Dependencies and integration points: depends on WiredTiger format-code handling, table schema creation, index creation, cursor lookup, and long-test mode (`wttest.islongtest`) for wider ranges.

Risks and edge cases: extreme unsigned/signed boundaries and powers of two are included to catch variable-length integer encoding bugs. Runtime grows substantially in long-test mode.

Test signals: every written value must round-trip through direct cursors and inverse index cursors with exact equality.
