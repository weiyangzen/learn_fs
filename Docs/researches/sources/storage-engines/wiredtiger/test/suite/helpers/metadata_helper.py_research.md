# sources/storage-engines/wiredtiger/test/suite/helpers/metadata_helper.py

Purpose: helper functions for reading WiredTiger metadata table IDs from Python tests.

Important APIs and control flow: `extract_id()` uses a regular expression to extract `,id=<digits>` from a metadata configuration string. `get_table_id()` opens a `metadata:` cursor through `WiredTigerCursor`, searches for a URI, raises `KeyError` if absent, and returns the parsed integer ID.

State and persistence behavior: reads metadata only; no persistent mutation.

Dependencies and integration points: depends on `re` and `helper.WiredTigerCursor`. Used by tests that need a numeric table/file ID, including lower-level storage or disaggregated helpers.

Risks: regex assumes the metadata config contains `,id=` with decimal digits. If the metadata format changes or `id` appears at the beginning without a leading comma, parsing fails.

Test signals: callers can assert nonmissing IDs and use them to locate related storage artifacts.
