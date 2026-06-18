# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/canonind.awk

This AWK script canonicalizes raw dictionary index output for use by `dict`.

Key behaviors:
- Expects one input file argument.
- Treats each raw line as an offset followed by index terms.
- Emits `term<TAB>offset` records.
- For terms with parenthesized alternates, emits both the version without the parenthesized text and the version including it.
- Writes temporary records to `junk`, then runs Plan 9 `sort -u -t'\t' +0f -1 +0 -1 +1n -2`.
- Removes the temporary file and exits.

Notable implementation details:
- Intended as a postprocessor for `mkindex`.
- Sort order folds first field while preserving exact field tie-breaking and numeric offset ordering.
