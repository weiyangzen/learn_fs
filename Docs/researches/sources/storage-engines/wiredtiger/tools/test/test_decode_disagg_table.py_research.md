# sources/storage-engines/wiredtiger/tools/test/test_decode_disagg_table.py

Purpose: integration-style unit test for decoding an encrypted disaggregated table JSONL fixture through the page-service adapter.

Important APIs and control flow: requires `DISAGG_KEYFILE`; otherwise it skips. It opens `binary_files/disagg_oplog.jsonl`, calls `page_service.process_disagg_table(disagg_file, DecodeOptions(keyfile=keyfile, bson=True))`, and asserts the returned summary has 2 delta pages, 6 full pages, and 8 total pages.

State and persistence behavior: read-only over the JSONL fixture and keyfile. The underlying page-service code creates temporary decryptor files.

Dependencies and integration points: exercises `page_service`, external `pagedecryptor`, `disagg.process_disagg_pages`, and the BSON decode path. It is sensitive to the MongoDB encryption-module toolchain being installed.

Risks: skipped by default without environment setup, so CI may not cover this path. It validates counts, not full decoded content or metadata-page root address behavior.

Test signals: when enabled, pass confirms decryptor integration and full/delta page classification for the sample table.
