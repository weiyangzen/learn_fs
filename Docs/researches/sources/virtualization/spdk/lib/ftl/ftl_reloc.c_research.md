# File Research: sources/virtualization/spdk/lib/ftl/ftl_reloc.c

Implements garbage-collection relocation from base-device bands into new writer bands.

Core model:
- `ftl_reloc` owns the current GC band, completed-band queue, max queue depth, halt state, and move objects.
- `ftl_reloc_move` owns one `ftl_rq` and transitions through `READ`, `PIN`, `WRITE`, `WAIT`, and `HALT`.

Main flow:
- Relocation selects GC bands with `ftl_band_get_next_gc`, walks valid-map bits, reads valid runs, pads request entries when needed, and advances the band iterator.
- After reads complete, it pins each valid LBA, retries pin failures by unpinning and reentering pin state, then queues the request to the GC writer.
- Write completion updates L2P from old addresses to new base addresses and unpins LBAs.
- Finished bands are freed if empty; otherwise errors push them back through close-state handling.
- Halt preserves upgrade behavior: if preparing upgrade and no free bands exist, relocation may keep running to reclaim one.

Architectural role: this is the base-device GC engine that supplies free bands and keeps valid data reachable while invalidating old locations.
