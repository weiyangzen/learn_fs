# File Research: sources/os/bsd/netbsd-src/lib/libedit/literal.h

## Purpose
Private header for libedit literal-display storage.

## Main Declarations
- `EL_LITERAL`: high-bit tag used to distinguish literal sentinel values from ordinary characters.
- `el_literal_t`: growable array of saved byte strings plus used/allocated counts.
- Lifecycle and lookup functions: `literal_init`, `literal_end`, `literal_clear`, `literal_add`, `literal_get`.

## Integration
`refresh.c` uses this mechanism when rendering encoded literal sequences. `el.h` embeds `el_literal_t` in `EditLine`.

## Risks And Notes
The tag uses a high `wint_t` bit. Portability depends on `wint_t` being able to carry that tag without colliding with valid characters.
