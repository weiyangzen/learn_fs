# sources/storage-engines/wiredtiger/test/suite/test_layered_schema01.py

## Purpose

This is the basic layered tree creation test. It verifies that creating a `layered:` URI creates the expected metadata entries for the logical layered object and its stable and ingest file constituents.

## Important APIs, Types, and Functions

The test uses `disagg_test_class` and a leader connection with verbose layered logging and `lose_all_my_data=true`. `StorageSource` is imported for constant access but not used in the test body. `check_metadata` opens `metadata:create` and asserts that a URI's metadata string contains an expected substring.

## Control Flow

The single test creates `layered:test_layered_schema01` with string key/value formats, then checks metadata for the layered URI, `file:test_layered_schema01.wt_ingest`, and `file:test_layered_schema01.wt_stable`. The expected substring is empty, so the test primarily asserts that each metadata entry exists and can be read.

## State, Persistence, and Dependencies

The persistent state is WiredTiger metadata for the layered table and its component files. Dependencies include `os`, `wiredtiger`, `wttest`, `helper_disagg`, and `wtscenario`, although scenarios are not used here. The integration point is the schema creation path for disaggregated layered tables.

## Risks and Test Signals

The risk is a schema create regression where the layered wrapper exists without one of its component files, or metadata lookup behavior changes. The signal is minimal but foundational: all expected URIs must exist in metadata immediately after create.
