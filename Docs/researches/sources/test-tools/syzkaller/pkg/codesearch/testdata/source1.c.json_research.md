# sources/test-tools/syzkaller/pkg/codesearch/testdata/source1.c.json

Purpose: Golden database for `source1.c`.

Important APIs/types/functions: One static function definition, `same_name_in_several_files`, with body and comment ranges.

Control flow: Static JSON.

State and persistence behavior: Persists expected static duplicate-symbol metadata.

Dependencies/integration points: Merged into the codesearch test database to test duplicate symbol lookup against `source2.c` and `source0.h`.

Risks: Static flag correctness matters for reference filtering. Line edits require golden updates.

Test signals: Confirms extraction of static function and comment in a duplicate-name scenario.
