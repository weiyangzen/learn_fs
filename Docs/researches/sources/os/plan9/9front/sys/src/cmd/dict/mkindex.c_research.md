# File Research: sources/os/plan9/9front/sys/src/cmd/dict/mkindex.c

Index seed generator for new dictionary backends.

Key elements:
- Opens a dictionary data file from `dicts[]`.
- Walks entries from offset 0 to EOF using the selected dictionary `nextoff`.
- Calls selected dictionary `printentry(e, 'h')` to extract headwords.
- Emits `offset<TAB>headword` pairs to stdout.
- Supports `-d dictname` and `-D`.

Dependencies:
- Uses `dict.h`, `dicts[]`, and adapter callbacks.
- Reuses output globals expected by adapter code.

Research notes:
- The header comment documents the workflow for adding a new dictionary: implement `nextoff` and headword printing, add `dicts[]`, run `mkindex`.
- Unlike runtime `dict`, this emits offset first and expects later canonicalization.
