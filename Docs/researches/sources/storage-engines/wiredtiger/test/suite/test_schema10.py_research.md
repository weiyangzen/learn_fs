<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_schema10.py -->
# sources/storage-engines/wiredtiger/test/suite/test_schema10.py

Purpose: validates that `session.create` rejects URI types with an empty object name.

Important APIs/types/functions: `test_schema10` uses `make_scenarios`, `wiredtiger.WiredTigerError`, and `assertRaisesWithMessage`. Scenarios cover `colgroup:`, `file:`, `index:`, `layered:`, and `table:`.

Control flow: for each URI prefix with no name, call `session.create(self.uri, "key_format=S,value_format=S")` and expect a `WiredTigerError` matching `URI requires a non-empty name`.

State and persistence behavior: no persistent objects should be created; the test is purely validation of URI parsing and schema admission control.

Dependencies/integration points: covers the schema dispatch path shared by multiple URI kinds, including layered objects. Risks are minimal but error text is asserted exactly by regex. Test signal is rejection before any object creation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_schema10.py -->
