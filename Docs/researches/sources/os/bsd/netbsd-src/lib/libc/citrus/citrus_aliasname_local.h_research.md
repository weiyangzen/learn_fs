# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_aliasname_local.h

Small internal helper header for locale/encoding alias handling.

Key behavior:
- `__unaliasname(dbname, alias, buf, bufsize)` performs a case-sensitive `_lookup_simple` query.
- `__isforcemapping(name)` checks whether a name equals `/force` case-insensitively through `_bcs_strcasecmp`.

Dependencies:
- Expects Citrus lookup aliases and BCS string comparison macros from surrounding includes.
- Used by locale category loaders that need alias resolution without exposing public API.
