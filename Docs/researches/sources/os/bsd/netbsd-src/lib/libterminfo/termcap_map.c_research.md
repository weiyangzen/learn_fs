# File Research: sources/os/bsd/netbsd-src/lib/libterminfo/termcap_map.c

Static mapping table from termcap IDs to internal terminfo capability IDs.

Key contents:
- Defines `TENTRY` with:
  - two-character termcap ID,
  - corresponding `TICODE_*` index.
- Provides three static mapping arrays:
  - `_ti_cap_flagids`
  - `_ti_cap_numids`
  - `_ti_cap_strids`
- Includes standard mappings and NetBSD extensions.
- Used by:
  - `termcap.c` for runtime termcap lookup and conversion,
  - `genthash` for hash generation,
  - `genman` for generated manual tables.

Role in subsystem:
- Single source of truth for termcap-to-terminfo compatibility mapping.
