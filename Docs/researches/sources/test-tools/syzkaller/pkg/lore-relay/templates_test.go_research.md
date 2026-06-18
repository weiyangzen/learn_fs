## sources/test-tools/syzkaller/pkg/lore-relay/templates_test.go

Purpose: golden tests for Lore relay template rendering.

Important APIs/types/functions: `flagWrite` and `TestRender`.

Control flow: reads JSON input fixtures, renders bodies/subjects, compares against expected output files, and can rewrite expected files with `-write_lore_tests`.

State and persistence: optional golden file rewrites when flag is set.

Dependencies and integration: covers template data conversion from dashboard poll results.

Risks: golden tests are sensitive to whitespace and template wording.

Test signals: good regression coverage for user-visible email output.
