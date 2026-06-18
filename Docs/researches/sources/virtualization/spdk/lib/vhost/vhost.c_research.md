# File Research: sources/virtualization/spdk/lib/vhost/vhost.c

This file implements common SPDK vhost controller and virtio-blk transport management.

Global state includes the allowed vhost core mask, a global vhost mutex, a list of created virtio-blk transports, a finalize callback, an RB tree of vhost devices keyed by name, and a registry of available virtio-blk transport operation tables.

`spdk_vhost_dev_next()` and `spdk_vhost_dev_find()` enumerate and look up devices in the RB tree. `vhost_parse_core_mask()` validates a requested cpumask is inside the SPDK environment core mask and nonempty, defaulting to the global mask when no mask string is supplied.

`vhost_dev_register()` validates name and cpumask, locks global vhost state, rejects duplicate names, stores the controller name, selects backend construction by backend type, and inserts the device into the RB tree. SCSI backends call `vhost_user_dev_create()`, while block backends call `virtio_blk_construct_ctrlr()`. `vhost_dev_unregister()` dispatches to the matching backend destroy/unregister path, removes the RB tree entry, frees the name, and invokes a pending fini callback when the last device is gone.

Accessors and operations expose device name, cpumask, backend info JSON, backend removal, and interrupt coalescing get/set. `spdk_vhost_lock()`, `spdk_vhost_trylock()`, and `spdk_vhost_unlock()` wrap the global mutex.

Initialization/finalization is split by backend. `spdk_vhost_scsi_init()` initializes vhost-user support and builds the core mask. `spdk_vhost_blk_init()` creates the default `vhost_user_blk` virtio-blk transport and builds the core mask. `spdk_vhost_scsi_fini()` starts vhost-user fini, then `vhost_fini()` removes remaining devices. `spdk_vhost_blk_fini()` destroys virtio-blk transports recursively.

Config JSON helpers emit controller replay RPCs and coalescing settings for SCSI and block devices. Block config also emits non-default virtio-blk transport creation RPCs, skipping the always-created `vhost_user_blk` transport.

Virtio-blk transport APIs register operation tables, create one instance per transport name, enumerate transports, dump transport options, find a target transport by name, and destroy transports through their ops.

Important invariants are global mutex protection around the device RB tree, backend-type dispatch consistency, no duplicate controller or transport names, and delayed finalize callback execution until devices/transports have been removed.
