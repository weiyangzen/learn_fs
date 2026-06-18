# sources/test-tools/syzkaller/pkg/codesearch/testdata/global_vars.c.json

Purpose: Golden codesearch database for `global_vars.c`.

Important APIs/types/functions: Contains definitions for `some_function`, `global_var`, `local_to_file_var`, `macro_var`, and `static_macro_var`, with kinds, types, body line ranges, and static markers.

Control flow: This is static JSON data read by golden tests; it has no executable flow.

State and persistence behavior: Persists expected clangtool output for this fixture. It is source-of-truth for regression comparison unless regenerated with `-update`.

Dependencies/integration points: Loaded by `tooltest.LoadOutput` and compared by `tooltest.TestClangTool`.

Risks: Golden line ranges are sensitive to fixture edits. It intentionally omits the local variable inside `some_function`, so extractor changes that include locals would require semantic review.

Test signals: Confirms global-variable extraction, static tracking, and macro-defined variable extraction.
