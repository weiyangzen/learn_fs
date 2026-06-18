# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/rev.awk

Tiny AWK helper for two-field tabular dictionary/index data. If a record has exactly two fields, it prints them reversed as `$2<TAB>$1`. Otherwise it prints `ERROR ` plus the original record.

Likely used while generating reverse lookup indexes. It assumes AWK’s default field splitting unless the caller sets `FS`.

Risks: records with embedded whitespace or more than two fields are treated as errors.
