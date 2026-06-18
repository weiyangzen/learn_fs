# sources/storage-engines/wiredtiger/tools/test/test_decode_disagg_delta_chain.py

Purpose: unit test for decoding a disaggregated delta-chain log through the top-level binary decoder.

Important APIs and control flow: appends the tools directory to `sys.path`, imports `wt_binary_decode` and `DecodeOptions`, locates `binary_files/disagg_delta_chain.log`, captures stdout with `contextlib.redirect_stdout`, calls `wt_binary_decode.wtdecode(log_path, DecodeOptions(disagg=True, dumpin=True))`, then asserts non-empty output, one full-image magic string, and exactly ten delta magic strings.

State and persistence behavior: read-only over the fixture log. It captures output in memory and writes nothing persistent.

Dependencies and integration points: exercises `wt_binary_decode`, `mdb_log_parse`, `file_format`, `disagg` mode page parsing, and `btree_format` disaggregated block headers.

Risks: asserts on formatted output strings rather than structured decode results, so wording changes can break the test. It does not assert checksum-chain diagnostics or decoded cell content.

Test signals: pass confirms the fixture is available and the decode stack recognizes base and delta block magic values in the expected counts.
