# File Research: sources/virtualization/guestfs-tools/gnulib/lib/argmatch.c

Gnulib argument string matcher.

Key functions:
- `argmatch`: matches an input string against a null-terminated argument list, allowing unambiguous abbreviations.
- Ambiguity can be resolved through value equivalence in `vallist`.
- Returns index, `-1` for invalid, `-2` for ambiguous.
- `argmatch_invalid`: prints invalid or ambiguous argument message.
- `argmatch_valid`: prints valid arguments, grouping adjacent synonyms.
- `__xargmatch_internal`: failure-reporting wrapper that calls a supplied exit function.
- `argmatch_to_argument`: maps a value back to its first argument string.

Includes a `TEST` block for backup-option matching.

Research relevance: generic CLI parsing helper for constrained option values.
