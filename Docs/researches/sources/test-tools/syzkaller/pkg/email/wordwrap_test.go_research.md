# sources/test-tools/syzkaller/pkg/email/wordwrap_test.go

Purpose: `wordwrap_test.go` verifies `WordWrap` and `visualLength` formatting contracts.

Important tests: `TestWordWrap` covers empty input, zero width, no wrap, simple wrap, exact width, long words, preserving paragraphs/blocks/list markers/quotes, indentation on wrapped lines, trailing-space removal, tab-aware wrapping, preserving internal spaces and tabs, final newline preservation, stack-trace text, and non-ASCII rune counting. `TestVisualLength` validates tab-stop calculations from several offsets and mixed strings.

Control flow and state: tests are table-driven and compare exact strings with `testify/require`.

Dependencies and integration: these tests define the output expected by any email text formatting caller.

Risks/test gaps: tests do not cover East Asian wide runes or combining marks, matching the implementation's simple rune-width model. Otherwise they provide strong regression coverage for wrapping semantics.
