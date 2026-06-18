# File Research: sources/virtualization/spdk/lib/ftl/ftl_l2p_flat.h

## Purpose
Declares the flat L2P backend API.

## API
Provides init/deinit, pin/unpin, get/set, trim, clear, restore, persist, process, halt-state, halt, and resume functions matching the backend dispatch layer in `ftl_l2p.c`.

## Dependencies
Relies on `struct spdk_ftl_dev`, `struct ftl_l2p_pin_ctx`, `ftl_l2p_cb`, and `ftl_addr` declarations from included callers.
