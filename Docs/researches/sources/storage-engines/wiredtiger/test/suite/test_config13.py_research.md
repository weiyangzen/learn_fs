<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config13.py -->
# sources/storage-engines/wiredtiger/test/suite/test_config13.py

Purpose: asserts that fixed-length column-store tables are rejected because FLCS is no longer supported.

Important APIs and control flow: `test_create_flcs()` attempts `session.create('table:flcs', 'value_format=8t,key_format=r')` and expects `WiredTigerError` with a fixed-length column-store deprecation message.

State, persistence, and dependencies: no table should be persisted on success because creation fails. Dependencies are the WiredTiger Python API, `wttest`, and create-time format validation.

Integration points: guards the public `session.create` API against accidentally re-enabling `8t` FLCS table creation.

Risks and test signals: this is intentionally narrow and message-sensitive. A pass is the exact rejection path; a failure would indicate either changed error text or unsupported FLCS creation becoming possible.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config13.py -->
