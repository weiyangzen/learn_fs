# File Research: sources/os/plan9/plan9/sys/src/cmd/abaco/charsets.awk

Generator for Abaco charset alias table entries.

Key responsibilities:
- Reads IANA `character-sets` text and a Plan 9 `tcs` mapping file.
- Records each charset `Name:` and non-`none` `Alias:`.
- Emits C initializer pairs mapping aliases to Plan 9 `tcs` encoding names.
- Lowercases charset names and aliases.

Dependencies:
- Intended to generate data included by `tcs.h`.
- Expects exactly two input files.

Notable risks:
- Parsing is line-oriented and depends on IANA text formatting.
