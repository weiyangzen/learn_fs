# sources/storage-engines/wiredtiger/test/suite/test_layered_config08.py

Purpose: verifies compaction APIs are rejected in disaggregated storage mode with clear `Operation not supported` errors.

Important APIs/types/functions: uses `DisaggConfigMixin`, `session.compact`, `assertRaisesWithMessage`, `wiredtiger.WiredTigerError`, and `skip_for_hook("tiered")` because tiered tables do not support compaction.

Control flow: under a disaggregated connection, the test calls `session.compact('table:test_layered_config08')` and `session.compact(None, 'background=true')`, expecting both to raise unsupported-operation errors.

State and persistence behavior: no durable data is created. The test validates API gating before any compaction state is started.

Dependencies/integration points: disaggregated connection configuration, compact API dispatch, background compact validation, and error propagation.

Risks: the named table is not created; the intended signal is that disaggregated mode rejects compact before object-specific lookup. If validation order changes, the test may need to create a table first.

Test signals: pass means both targeted and background compaction are disabled in disaggregated mode.
