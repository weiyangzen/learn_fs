# sources/test-tools/syzkaller/pkg/email/wordwrap.go

Purpose: `wordwrap.go` wraps plain text to a visual width while preserving existing line breaks, indentation, spacing between words, tabs, and long words.

Important APIs/functions: `WordWrap(text string, width int) string` is the public formatter. `visualLength(p int, s string) int` computes visual column position after adding a string, expanding tabs to 8-column stops and counting runes rather than bytes.

Control flow and state: width is clamped to at least 1. The function splits input by newline, preserves each line's leading whitespace, and then repeatedly extracts original whitespace and word segments from the trimmed remainder. A word preceded by spaces is either appended if it fits or moved to a new indented line with the separating spaces dropped. Empty lines are preserved. Single words longer than width are not split.

Dependencies and integration: this file uses only `strings` and `unicode`. It is suitable for formatting generated email text before sending.

Risks: trailing spaces are dropped when only whitespace remains. It treats all non-tab runes as width 1, so East Asian wide characters and combining marks are approximate. Tests in `wordwrap_test.go` cover indentation, tabs, trailing spaces, newlines, quotes, stack traces, and non-ASCII rune counting.
