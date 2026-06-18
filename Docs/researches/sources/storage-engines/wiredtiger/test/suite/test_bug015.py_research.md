# sources/storage-engines/wiredtiger/test/suite/test_bug015.py

Purpose: regression for WT-2162, where dropping and recreating indexes in a particular lexical order triggered a NULL pointer dereference.

Important APIs/types/functions: `wttest.WiredTigerTestCase`, `session.create`, `session.drop`, table URI `table:test_bug015`, and index URIs `index:test_bug015:aab` and `index:test_bug015:aaa`.

Control flow: create a table with columns `(k,v)`, create two indexes on column `v`, drop/recreate `aab`, then drop/recreate `aaa`.

State/persistence behavior: manipulates metadata and index handles only; no row data is inserted. The test targets index lifecycle state and namespace ordering.

Dependencies/integration: uses the schema/index metadata subsystem and forced drops through the Python API.

Risks/test signals: no assertions are needed; success means no crash or exception during the exact DDL sequence.
