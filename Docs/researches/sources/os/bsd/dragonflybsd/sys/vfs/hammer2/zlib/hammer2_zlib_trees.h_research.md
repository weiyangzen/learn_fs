# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_trees.h

Source read: complete file, 128 lines.

Purpose: Generated deflate tree constants used by `hammer2_zlib_trees.c` when not building tables at runtime.

Key contents:
- `static_ltree[L_CODES+2]` contains fixed literal/length tree code/length pairs.
- `static_dtree[D_CODES]` contains fixed distance tree code/length pairs.
- `_dist_code[DIST_CODE_LEN]` maps normalized distances to distance code numbers.
- `_length_code[MAX_MATCH-MIN_MATCH+1]` maps normalized match lengths to length code numbers.
- `base_length[LENGTH_CODES]` and `base_dist[D_CODES]` define base values for extra-bit emission.

Integration:
- Included directly by `hammer2_zlib_trees.c`.
- Relies on `ct_data`, `uch`, `L_CODES`, `D_CODES`, `LENGTH_CODES`, `MAX_MATCH`, `MIN_MATCH`, and related constants from `hammer2_zlib_deflate.h`.

Risks and review notes:
- This is generated data; manual edits are risky unless regenerated with the matching generator mode.
- The arrays must stay consistent with deflate tables and extra-bit arrays in `hammer2_zlib_trees.c`.
