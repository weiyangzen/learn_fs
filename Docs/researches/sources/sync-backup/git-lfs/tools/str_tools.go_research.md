# sources/sync-backup/git-lfs/tools/str_tools.go

Purpose: string parsing and formatting helpers.

Important APIs/types/functions: `QuotedFields`, `Ljust`, `Rjust`, `Longest`, `Indent`, and `Undent`.

Control flow: `QuotedFields` uses a regexp to extract single-quoted, double-quoted, or non-space tokens. Justification copies the input slice and pads to the byte length of the longest string. `Indent` prepends tabs line-wise; `Undent` removes leading spaces/tabs at line starts.

State and persistence: package regexes only; no I/O.

Dependencies and integration points: useful for command/config parsing and formatted CLI output.

Risks: length calculations are byte-based, not display-width or rune-width based. Quote parsing is regexp-greedy and does not implement shell escaping. `Undent` removes all leading spaces/tabs, not just common indentation.

Test signals: `str_tools_test.go` covers quote variants, nested/mixed quotes, justification, indentation, and linebreak preservation.
