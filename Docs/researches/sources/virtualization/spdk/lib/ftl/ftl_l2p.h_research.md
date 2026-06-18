# File Research: sources/virtualization/spdk/lib/ftl/ftl_l2p.h

## Purpose
Declares the L2P mapping abstraction used by FTL core, writers, GC, and recovery.

## API
- Lifecycle: `ftl_l2p_init()`, `ftl_l2p_deinit()`.
- Pinning: `ftl_l2p_pin()`, `ftl_l2p_unpin()`, `ftl_l2p_pin_skip()`, `ftl_l2p_pin_complete()`.
- Mapping: `ftl_l2p_set()`, `ftl_l2p_get()`.
- Metadata operations: clear, trim, restore, persist, process.
- Flow control: halt, resume, is_halted.
- Update helpers: `ftl_l2p_update_cache()` and `ftl_l2p_update_base()`.

## Key Type
`struct ftl_l2p_pin_ctx` stores requested LBA/count, completion callback, callback context, and queue link for deferred pins.
