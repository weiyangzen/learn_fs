# File Research: sources/virtualization/guestfs-tools/gnulib/lib/argmatch.h

Header and macro framework for `argmatch`.

Exports:
- Core functions and macros: `ARGMATCH`, `XARGMATCH`, `ARGMATCH_VALID`, `ARGMATCH_TO_ARGUMENT`.
- `argmatch_exit_fn` and external `argmatch_die`.
- `ARGMATCH_DEFINE_GROUP`, a large macro that generates typed group-specific choice, value, argument, valid-list, doc-column, and usage functions.

Generated group behavior:
- Supports exact and unambiguous abbreviated matches.
- Treats multiple strings with equal typed values as synonyms.
- Can print localized valid argument lists and usage documentation.
- Wraps failures through `argmatch_invalid` and `argmatch_die`.

Research relevance: type-safe macro layer over string-to-enum style command option parsing.
