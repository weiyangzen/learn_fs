# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclbits.c

Command-list bitmap, transfer-map, and tile-cache writer support. `clist_bitmap_bytes` implements the command-list padding policy: compressed bitmaps keep full raster padding, narrow/one-line/spread bitmaps drop padding, and other uncompressed bitmaps drop padding only on the last scan line. `cmd_put_bits` allocates command buffer space, optionally tries CCITTFax or RLE compression, shortens commands when compression or padding choices reduce size, and returns the selected compression code or a limit error.

The tile-cache section hashes bitmap ids into the writer’s tile table, deletes cache entries with conservative dependent-entry deletion, and allocates tile slots from a bits cache. `clist_new_tile_params` chooses replicated tile dimensions under size/count constraints. `clist_change_tile` emits tile parameter and tile-bit commands per band, marking which bands know a cached tile. `clist_change_bits` does the analogous path for copy operations and can promote frequently reused character bitmaps to all bands, though the current threshold disables that by default.

The file is tightly bound to the bytecode and band-state definitions in `gxcldev.h`, plus compression streams from `scfx.h` and `srlx.h`.
