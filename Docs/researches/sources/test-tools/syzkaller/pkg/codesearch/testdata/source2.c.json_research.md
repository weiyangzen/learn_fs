# sources/test-tools/syzkaller/pkg/codesearch/testdata/source2.c.json

Purpose: Golden database for `source2.c`.

Important APIs/types/functions: One non-static function definition, `same_name_in_several_files`, with body and comment ranges.

Control flow: Static JSON.

State and persistence behavior: Persists expected duplicate global symbol metadata.

Dependencies/integration points: Merged into codesearch tests to check context-aware lookup against the static same-name function.

Risks: Golden line ranges are sensitive to comments/source edits.

Test signals: Confirms non-static duplicate symbol extraction.
