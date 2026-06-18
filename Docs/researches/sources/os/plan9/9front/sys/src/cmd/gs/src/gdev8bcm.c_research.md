# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdev8bcm.c

## Scope

Shared dynamic color-map implementation for 8-bit display devices.

## Key Behavior

- `gx_8bit_map_init` clears a hash table and sets maximum dynamic colors.
- `gx_8bit_map_rgb_color` hashes a 15-bit RGB key into an open-addressed map and returns either an index or a negative insertion slot.
- `gx_8bit_add_rgb_color` adds a previously missing RGB key and assigns the next dynamic color index.

## Dependencies

Uses declarations from `gdev8bcm.h` and Ghostscript color value types.

## Risks And Invariants

- The negative “not found” return encodes an insertion slot by subtracting from the end of the map array.
- Callers must honor `max_count`; the map table has capacity beyond the configured dynamic color count.
