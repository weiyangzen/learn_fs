# File Research: sources/os/plan9/9front/sys/src/cmd/dict/t.awk

AWK normalizer for index records containing “ or ” alternatives.

Key elements:
- For two-field records, prints unchanged unless the second field contains ` or ` and is not parenthesized as `(or...)`.
- Splits eligible alternatives on ` or ` and emits one record per alternative.
- Non-two-field records are printed unchanged.

Dependencies:
- Standalone AWK script.

Research notes:
- Used to expand alternate headword forms in index-generation pipelines.
