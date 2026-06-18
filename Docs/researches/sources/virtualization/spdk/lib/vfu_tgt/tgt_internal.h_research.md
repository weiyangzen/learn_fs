# File Research: sources/virtualization/spdk/lib/vfu_tgt/tgt_internal.h

This private header defines `struct spdk_vfu_endpoint`.

An endpoint stores its name, socket UUID/path, backend operation table, libvfio-user context, backend private context, accept and context pollers, attached state, MSI-X capability pointer, PCI config-space pointer, owning SPDK thread, and list linkage.

The structure is shared by endpoint management and RPC/backend integration. Its fields encode the endpoint lifetime model: one libvfio-user context, one SPDK thread, pollers on that thread, and backend private state controlled through `spdk_vfu_endpoint_ops`.
