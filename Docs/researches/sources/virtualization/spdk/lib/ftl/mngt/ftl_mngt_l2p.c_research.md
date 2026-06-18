# File Research: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_l2p.c

Thin management wrappers around L2P subsystem operations.

Provides steps for:
- `ftl_l2p_init`
- `ftl_l2p_deinit`
- `ftl_l2p_clear`
- `ftl_l2p_persist`
- `ftl_l2p_trim`
- `ftl_l2p_restore`

Asynchronous L2P callbacks use a shared `l2p_cb` that fails or advances the management step based on status. This file intentionally keeps sequencing in the management descriptor layer and delegates actual L2P behavior elsewhere.
