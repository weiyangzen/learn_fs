# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/doi.c

This file implements the DOI registry for `isakmpd`.

Key responsibilities:
- Maintains a global list of registered Domain of Interpretation handlers.
- Initializes the registry.
- Looks up a DOI by ID.
- Registers DOI handler structures.

Important functions:
- `doi_init()`: initializes the DOI list.
- `doi_lookup(u_int8_t doi_id)`: linear search by DOI ID.
- `doi_register(struct doi *doi)`: inserts a handler into the registry.

Dependencies:
- `struct doi` from `doi.h`.
- BSD list macros.

Research notes:
- This is a small dispatcher registry; most DOI-specific behavior lives behind the function pointers in `struct doi`.
