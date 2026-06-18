# File Research: sources/virtualization/spdk/lib/idxd/idxd_user.c

`idxd_user.c` implements the default user-space PCI IDXD backend. It enumerates IDXD PCI devices, claims devices, maps MMIO and work-queue BARs, programs groups and work queues directly, enables the device, initializes DSA or IAA-specific state, and registers an `spdk_idxd_impl` named `user`.

Device configuration maps `IDXD_MMIO_BAR` and `IDXD_WQ_BAR`, resets the device, reads version/capability registers, configures one group containing all engines and one work queue, writes WQ configuration for dedicated mode, full WQ size, max batch shift, max transfer shift, enabled state, and priority, then enables the device and WQ through command registers.

The probe path is serialized by `g_driver_lock`, calls the caller’s probe callback, claims accepted PCI devices, attaches them, and calls the attach callback. Attach determines device type from PCI ID: DSA devices use DSA operations, while IAA devices allocate a DMA AECS table and fill fixed Huffman tables required for RFC-1951 fixed compression. The attach path also enables PCI bus mastering, initializes the channel-count mutex, and calls the hardware configuration routine.

Destruction disables the device, unmaps BARs, detaches the PCI device, frees IAA AECS state when present, and frees the wrapper. Software-error dumping reads and logs the device SWERR register fields. Portal lookup returns the mapped work-queue BAR address.

Research notes: this backend owns hardware programming policy and currently configures one dedicated WQ. The IAA fixed Huffman tables are static data used to initialize AECS for compression. Error paths around BAR mapping/configuration are important because failed attach calls into the destructor for cleanup.
