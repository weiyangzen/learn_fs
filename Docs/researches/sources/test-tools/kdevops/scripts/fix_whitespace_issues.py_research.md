<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/fix_whitespace_issues.py -->
# sources/test-tools/kdevops/scripts/fix_whitespace_issues.py

Purpose: fixes trailing whitespace, missing final newline, and excessive blank lines in selected files.

Important APIs and functions: `fix_file_whitespace(file_path)` skips null-containing binaries, decodes text, removes trailing spaces/tabs while preserving `\n` or `\r\n`, limits blank runs to two lines, appends a final newline, writes back on modification, and returns fix messages. `main()` uses explicit paths or `git diff --name-only`, skips common binary suffixes, prints per-file fixes, and exits 0.

Control flow: path discovery, filtering, per-file transformation, write if changed, summary.

State and persistence: rewrites files in text mode with UTF-8 encoding when modified. It can normalize encoding for files decoded with ignored errors.

Dependencies and integration: standard library plus git. `scripts/style.Makefile` uses this script to fix modified files.

Risks: invalid UTF-8 bytes can be dropped on write. Default mode only touches modified files, while explicit paths can be broad. The blank-line reducer may alter intentional spacing in generated text or markdown. Test signals include fixtures for CRLF, final newline, trailing tabs, blank runs, binary skip, and no-op idempotence after a second run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/fix_whitespace_issues.py -->
