# File Research: sources/virtualization/spdk/lib/idxd/idxd_internal.h

`idxd_internal.h` defines private IDXD structures and helpers shared by the common datapath and backend implementations.

It provides the inline `movdir64b()` descriptor-write primitive, IDXD timing/config constants, DSA/IAA device type enum, batch metadata, per-channel state, PCI ID helper structure, operation/completion wrapper, backend implementation interface, and the common `spdk_idxd_device` structure.

`spdk_idxd_io_channel` stores the target device, portal address and offset, PASID state, current open batch, descriptor and operation pools, outstanding operations, and batch pool. `idxd_ops` wraps either DSA or IAA completion records, callback data, descriptor pointer, optional CRC/output-size destination, parent op pointer, and split-operation count; a static assertion fixes its size at 128 bytes.

`spdk_idxd_impl` abstracts backend-specific probing, destruction, software-error dumping, and portal address lookup. The `SPDK_IDXD_IMPL_REGISTER` constructor macro registers backend implementations at load time.

Research notes: this header is the private ABI between `idxd.c`, `idxd_user.c`, and `idxd_kernel.c`. Layout changes affect descriptor pool allocation, completion interpretation, and backend registration.
