# sources/storage-engines/wiredtiger/tools/test/test_decode_disagg_delta_page.py

Purpose: unit test for parsing a single disaggregated delta page binary fixture.

Important APIs and control flow: locates `binary_files/disagg_delta_oplog.bin`, wraps it in `binary_data.BinaryFile`, calls `btree_format.WTPage.parse(..., disagg=True)`, prints the page with BSON decoding enabled, and asserts page header fields, block disaggregated header fields, checksum flags, cell count, key/value cell roles, value data length, and a known start timestamp.

State and persistence behavior: read-only over the binary fixture; stdout printing is incidental.

Dependencies and integration points: directly tests `py_common.btree_format` and `py_common.binary_data` disaggregated page support, indirectly depending on optional BSON support for printed output only.

Risks: fixture-specific constants make the test precise but brittle to intentional fixture replacement. It does not verify the complete decoded BSON payload.

Test signals: pass validates delta magic/version/header-size/checksum parsing, page header decoding, cell extraction, and timestamp parsing for delta pages.
