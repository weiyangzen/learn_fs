# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdev8bcm.c

Dynamic color-map implementation for 8-bit display devices.

Key points:
- `gx_8bit_map_init` initializes a fixed-size open-addressing hash table.
- `gx_8bit_map_rgb_color` hashes a reduced 5-bit-per-channel RGB key and returns an existing color index or a negative insertion slot.
- `gx_8bit_add_rgb_color` inserts a new RGB key when space remains and returns its assigned dynamic index.
- Uses a prime-ish map size and spreader to reduce clustering.

Dependencies and interactions:
- Implements declarations from `gdev8bcm.h`.
- Shared by display drivers that need fast lookup for dynamic 8-bit colormaps.

OS/filesystem relevance:
- None; purely in-memory color lookup support.
