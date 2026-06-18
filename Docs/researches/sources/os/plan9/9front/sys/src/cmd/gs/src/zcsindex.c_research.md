# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zcsindex.c

Implements Indexed color-space setup and mapped lookup-cache loading.

Key behavior:
- Defines `.setindexedspace`, where the current color space becomes the Indexed base space.
- Validates a four-element Indexed color-space array and `hival` range.
- Supports string lookup tables directly, tolerating extra bytes but requiring at least the needed table length.
- Supports procedural lookup tables by allocating a `gs_indexed_map` and scheduling continuation-driven sampling of each index.
- `indexed_map1` stores generated component values into the map as the tint/index procedure runs.
- `zcs_begin_map` is shared utility code for Indexed and tint-map style color-space loaders.

Dependencies:
- Uses graphics color-space APIs, interpreter e-stack continuations, numeric parameter helpers, and VM-space-aware allocation.

Research notes:
- The explicit `memmove` around base-space copying avoids strict-aliasing/compiler misoptimization problems documented in comments.
