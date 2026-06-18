# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/t.awk

AWK helper that expands two-field rows whose second field contains ` or `. If `$2` contains ` or ` and does not contain `(or`, it splits `$2` on ` or ` and emits one `$1<TAB>variant` row per piece. All other two-field rows pass through unchanged; non-two-field rows also pass through unchanged.

Likely used in index preparation to split alternate forms while preserving parenthesized literal “or” text.

Risks: depends on AWK field splitting and simple regex heuristics; values with tabs/spaces outside the expected format can be mis-split or passed through unexpectedly.
