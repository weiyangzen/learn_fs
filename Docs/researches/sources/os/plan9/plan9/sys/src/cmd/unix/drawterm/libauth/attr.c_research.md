# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/attr.c

This file implements auth attribute list formatting, parsing, lookup, copying, and cleanup.

Key behavior:
- `_attrfmt` formats linked `Attr` lists with quoting for query attributes.
- `_mkattr`, `_copyattr`, `_delattr`, `_findattr`, `_strfindattr`, and `_freeattr` manage attribute lists.
- `_parseattr` parses `name=value` and query-style attributes from a string.
- `cleanattr` removes duplicate attributes by keeping later entries.

Important details:
- Attribute values are parsed with Plan 9 tokenization/quoting rules.
- `Attr.type` controls plain versus query attribute output.
