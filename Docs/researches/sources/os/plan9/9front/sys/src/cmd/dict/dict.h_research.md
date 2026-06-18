# File Research: sources/os/plan9/9front/sys/src/cmd/dict/dict.h

Shared API and private-use rune definitions for the `dict` command modules.

Key elements:
- Defines private-use sentinel runes for output suppression, tags, special names, paragraphs, accent ligature states, and multi-rune expansions.
- Defines `Entry`, `Assoc`, `Nassoc`, and `Dict`.
- `Dict` binds a dictionary name/description/data path/index path to callbacks: `nextoff`, `printentry`, and `printkey`.
- Declares common utility functions for lookup, output formatting, folding, ligature handling, and translation-table stack management.
- Declares all dictionary adapter callbacks used by `utils.c`.

Dependencies:
- Requires Plan 9 `Rune` and `Biobuf` types from including files.
- Shared by all dictionary source files in this group.

Research notes:
- The private-use constants are internal markup tokens, not output characters.
- The adapter contract is narrow: find next entry offset, print an entry for command mode, and print pronunciation/help key.
