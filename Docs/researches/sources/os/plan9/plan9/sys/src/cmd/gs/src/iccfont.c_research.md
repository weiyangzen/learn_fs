# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iccfont.c

Provides initialization support for compiled fonts. It converts compact C font tables into interpreter refs, dictionaries, arrays, names, strings, and parsed objects.

Main components:
- `str_enum` and `key_enum`: walk compact string/key arrays.
- `cfont_next_string`: decodes inline string encodings, null markers, and parsed-object strings.
- `cfont_put_next`: resolves encoded or string keys to names and stores dictionary entries.
- `cfont_*_create`: create dictionaries and arrays with ref/string/number/name/scalar contents.
- `cfont_ref_from_string`: uses the scanner to parse an object from a string.
- `ccfont_procs`: procedure vector passed to compiled-font initializers.
- `.getccfont` operator: returns compiled font count or builds a requested font object.

This file bridges generated C font assets into PostScript VM objects.
