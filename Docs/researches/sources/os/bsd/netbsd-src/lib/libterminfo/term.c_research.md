# File Research: sources/os/bsd/netbsd-src/lib/libterminfo/term.c

Loads and decodes compiled terminal descriptions.

Key responsibilities:
- Defines default terminfo database path `/usr/share/misc/terminfo`.
- Includes generated `compiled_terms.c` for built-in fallback descriptions.
- Decodes serialized terminfo records into `TERMINAL` fields:
  - flags,
  - numeric capabilities,
  - string capabilities,
  - user-defined capabilities.
- Handles type-1 and type-3 records.
- Reads cdb-backed terminfo databases via `cdbr`.
- Resolves alias records.
- Searches multiple sources:
  - inline `$TERMINFO`,
  - inline `$TERMCAP` converted through `captoinfo`,
  - `TERMINFO_DIRS`,
  - `$HOME/.terminfo`,
  - system terminfo database,
  - embedded compiled terms.
- Validates loaded records against requested name or aliases.

Important functions:
- `_ti_getterm`
- `_ti_readterm`
- `_ti_findterm`
- `_ti_dbgetterm`
- `_ti_dbgettermp`
- `_ti_checkname`

Role in subsystem:
- Main terminfo database/runtime loader.
