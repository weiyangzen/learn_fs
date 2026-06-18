# sources/storage-engines/wiredtiger/test/suite/test_compact15.py

Purpose: validates foreground compaction API requires a URI while allowing a valid URI.

Important APIs and types: `WiredTigerTestCase`, `session.compact`, `wiredtiger.WiredTigerError`, `assertRaisesWithMessage`, and `make_scenarios`.

Control flow: create a table, then either call `session.compact(self.uri, None)` for the valid scenario or call `session.compact(None, None)` and expect an error for the invalid scenario.

State and persistence behavior: this is API validation rather than data persistence. It protects the distinction between foreground compaction, which requires a target URI, and background compaction, which uses `None` with `background=true`.

Dependencies and integration points: compaction configuration parser and tiered hook behavior. Tiered hook is skipped.

Risks: valid URI scenario does not verify compaction work occurred; it only checks the call is accepted.

Test signals: valid URI compaction returns successfully; missing URI raises with `Compaction requires a URI`.
