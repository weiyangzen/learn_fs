# File Research: sources/os/bsd/netbsd-src/lib/libterminfo/genthash

Shell generator for termcap compatibility hash functions.

Key responsibilities:
- Reads `termcap_map.c`.
- Extracts termcap IDs from `_ti_cap_flagids`, `_ti_cap_numids`, and `_ti_cap_strids`.
- Uses `nbperf` to generate:
  - `_t_flaghash`
  - `_t_numhash`
  - `_t_strhash`

Role in subsystem:
- Accelerates mapping of two-character termcap IDs to internal terminfo capability indexes.
