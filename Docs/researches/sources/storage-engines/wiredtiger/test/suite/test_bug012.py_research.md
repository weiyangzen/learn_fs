# sources/storage-engines/wiredtiger/test/suite/test_bug012.py

Purpose: validates configuration error handling for illegal collator, key format, value format, and compressor names. It ensures invalid configuration strings fail predictably rather than being accepted or failing later.

Important APIs/types/functions: `wiredtiger.WiredTigerError`, `wttest.WiredTigerTestCase.assertRaisesWithMessage`, and `session.create`. The imported `ComplexDataSet` is unused.

Control flow: four independent test methods each call `session.create('table:A', invalid_config)` inside `assertRaisesWithMessage`. Expected messages are `/unknown collator/`, `/Invalid type/`, and `/unknown compressor/`.

State/persistence behavior: no durable data should be created. The tested state is parser/extension registry validation before object creation.

Dependencies/integration: exercises the public schema creation path and error-message contracts for extension-driven configuration fields.

Risks/test signals: depends on stable error message fragments. A false negative can occur if validation still fails correctly but wording changes.
