# sources/test-tools/syzkaller/pkg/codesearch/testdata/mm/slub.c

Purpose: Two-line fixture used for `read-file` and directory listing tests.

Important APIs/types/functions: No C symbols; contains comments/text only.

Control flow: None.

State and persistence behavior: Source text is the state. It intentionally produces an empty codesearch JSON database.

Dependencies/integration points: Used by `ReadFile` tests to verify line formatting and nested file access.

Risks: Because it defines no entities, `FileIndex` should distinguish "file exists with no definitions" from missing file by reading the file first.

Test signals: Paired with empty `slub.c.json` and read-file golden queries.
