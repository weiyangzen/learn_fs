# sources/test-tools/syzkaller/pkg/covermerger/lines_matcher_test.go

Purpose: validates line-to-line mapping across simple file edits.

Important APIs/types/functions: package test text fixtures and `TestMatching`.

Control flow: table cases build matchers for identical text, insertion before the source line, source-line removal, and source-line text change. Each asserts `SameLinePos` for line 0.

State and persistence: in-memory strings only.

Dependencies and integration: uses testify assertions and the real `makeLineToLineMatcher`.

Risks: tests focus on the first line only and do not cover repeated lines, later-line changes, out-of-range indexes, or one-based line inputs from coverage records.

Test signals: basic regression signal for the exact-match-only mapping policy.
