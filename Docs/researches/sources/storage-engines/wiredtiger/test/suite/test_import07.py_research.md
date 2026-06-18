# sources/storage-engines/wiredtiger/test/suite/test_import07.py

Purpose: verifies import is rejected for unsupported data-source URI prefixes, specifically `colgroup:` and `index:`.

Important APIs and functions: `test_import07` inherits `test_import_base` and uses scenarios for `prefix='colgroup:'` and `prefix='index:'`. It builds a valid-looking import config from example table metadata but applies it to an unsupported URI.

Control flow: the test populates/checkpoints generated tables, grabs any `table:` metadata config, builds `import=(enabled,repair=false,file_metadata=(...))`, prefixes `original_db_file` with the scenario data source, and calls `session.create`. The create must fail before file existence matters.

State and persistence behavior: no target file state is required; this validates import routing/validation based on URI data source.

Dependencies and integration points: depends on metadata cursor iteration, import configuration parser, and data-source dispatch validation.

Risks and edge cases: if WiredTiger adds import support for colgroups or indexes, this test's expected behavior must change. It does not validate `file:` or `table:` success paths because other import tests cover those.

Test signals: `session.create` raises `WiredTigerError` matching `/Operation not supported/`.
