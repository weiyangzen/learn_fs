# File Research: sources/os/linux/linux-stable/fs/gfs2/gfs2.h

## Scope

This small umbrella header defines basic constants shared by the GFS2 implementation.

## APIs And Constants

- Defines boolean-like create controls: `NO_CREATE` and `CREATE`.
- Defines force controls: `NO_FORCE` and `FORCE`.
- Defines `GFS2_FAST_NAME_SIZE` as 8.

## Dependencies And Role

- Included by implementation files as a lightweight common header before deeper subsystem headers.
- `CREATE` / `NO_CREATE` are used by glock lookup/creation call sites, including `gfs2_glock_get()` callers.

## Risks And Invariants

- The values are intentionally simple integer constants, not typed enums exposed outside this subsystem.
- Changing `CREATE` / `NO_CREATE` values would affect call sites that pass them as `int create` flags.
