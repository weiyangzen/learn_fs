# File Research: sources/virtualization/spdk/lib/ftl/ftl_l2p_cache.h

## Purpose
Declares the cached L2P backend API and metadata object names.

## Contents
- Metadata names: `l2p_l1`, `l2p_l2`, and `l2p_l2_ctx`.
- Declares cached backend functions for init/deinit, pin/unpin, get/set, trim, clear, restore, persist, process, halt/resume, and halt-state query.

## Dependencies
Relies on types from FTL core/L2P headers included by callers.
