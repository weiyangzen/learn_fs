# File Research: sources/os/bsd/netbsd-src/lib/libterminfo/term_private.h

Private internal header for `libterminfo`, `tic`, and `infocmp`.

Key responsibilities:
- Documents NetBSD’s private serialized terminfo database format:
  - type 1 records,
  - type 2 alias records,
  - type 3 records with 32-bit numerics.
- Defines record type constants:
  - `TERMINFO_RTYPE_O1`
  - `TERMINFO_ALIAS`
  - `TERMINFO_RTYPE`
- Defines absent/cancelled values and validation macros.
- Defines full private `TERMINAL`, adding:
  - backing serialized area,
  - user-defined capabilities,
  - saved output speed,
  - tparm buffer,
  - static tparm variables,
  - alias string.
- Defines `TERMUSERDEF`, `TBUF`, and `TIC`.
- Declares internal lookup, loading, compilation, flattening, and encoding helpers.
- Provides inline little-endian encode/decode helpers for 16-bit, 32-bit, strings, and typed numeric storage.

Role in subsystem:
- Shared implementation contract for terminfo decoding, compilation, lookup, and parameter expansion.
