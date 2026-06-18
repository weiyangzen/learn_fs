# sources/storage-engines/wiredtiger/tools/test/test_decode_page.py

Purpose: unit test for decoding one ordinary WiredTiger page from a text hex dump fixture.

Important APIs and control flow: `load_page_bytes()` reads `binary_files/WiredTiger01.txt` and decodes it with `mdb_log_parse.encode_bytes()`. The test wraps bytes in `BinaryFile`, parses a `WTPage` with `skip_data=True`, then asserts page header fields (`recno`, `write_gen`, `mem_size`, entries, type, flags, version) and block header fields (`disk_size`, checksum, flags).

State and persistence behavior: read-only fixture use and in-memory decode only.

Dependencies and integration points: validates `mdb_log_parse.encode_bytes()`, `binary_data.BinaryFile`, and `btree_format.WTPage.parse()` for standard blocks.

Risks: header-only parsing does not validate cell decoding or payload display. The fixture constants encode one page layout and do not cover compressed or corrupted blocks.

Test signals: pass confirms the basic non-disaggregated page parser still matches the known fixture.
