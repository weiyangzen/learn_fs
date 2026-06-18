# sources/test-tools/syzkaller/pkg/codesearch/testdata/source1.c

Purpose: Duplicate-name C fixture defining a static version of `same_name_in_several_files`.

Important APIs/types/functions: Static function `same_name_in_several_files`.

Control flow: Empty function body with an explanatory comment.

State and persistence behavior: Expected database state lives in `source1.c.json`, with `is_static: true`.

Dependencies/integration points: Tests context-aware definition resolution and static visibility in `codesearch.findDefinition` and `FindReferences`.

Risks: Static duplicate-name behavior is explicitly subtle; queries from other files should not resolve to this definition except through weak fallback rules.

Test signals: Golden JSON confirms static function extraction and comment range.
