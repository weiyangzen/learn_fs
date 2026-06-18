# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iccfont.c

Implements initialization support for compiled fonts.

Key behavior:
- Defines string and key enumerators for compact compiled-font key/value arrays.
- `cfont_next_string` decodes compact string arrays, including null markers and object-from-string markers.
- `cfont_put_next` creates dictionary entries from encoded keys or string keys and stores supplied values.
- Provides helpers to create dictionaries with general refs, string/null values, or scalar/array number values.
- Provides helpers to create name arrays, string arrays, scalar arrays, names, and parsed refs from strings.
- Parsing uses scanner state and a string stream to convert compact text to a PostScript object.
- Builds a `cfont_procs` procedure vector passed to compiled-font initialization code.
- Defines `.getccfont`, returning font count for null input or constructing a selected compiled font object for an integer index.
- Validates compiled font procedure table version through `ccfont_fprocs`.
- Registers operator table `ccfonts_op_defs`.

Research notes:
- This file bridges generated compiled-font C data into live interpreter refs.
- It uses interpreter allocation and dictionary APIs, so save/VM attributes are part of object creation.
