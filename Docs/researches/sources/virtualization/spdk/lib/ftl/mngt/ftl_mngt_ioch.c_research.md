# File Research: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_ioch.c

Manages FTL IO channel registration and per-thread channel lifecycle.

`io_channel_create_cb` allocates an `ftl_io_channel`, creates a per-channel map mempool, completion/submission rings sized from `user_io_pool_size`, registers an IO-channel poller, and posts registration to the core thread. The channel is then available through `ftl_io_channel_get_ctx`.

Destroy path unregisters the poller on the owning thread and posts cleanup to the core thread, where queues and mempools are freed and the channel is removed from `dev->ioch_queue`.

Management steps register/unregister the SPDK IO device and get/put the core thread's own IO channel. Unregistration is asynchronous and resumes the management process via callback.
