# File Research: sources/virtualization/spdk/lib/nvme/nvme_stubs.c

Provides compile-time fallback stubs for optional NVMe features when SPDK is built without specific configuration flags.

Covered feature gates:
- `!SPDK_CONFIG_NVME_CUSE`: CUSE controller/namespace naming, register, unregister, and namespace update APIs log unsupported errors. Functions returning status use `-ENOTSUP`; namespace update is `void` and only logs.
- `!SPDK_CONFIG_RDMA`: `spdk_nvme_rdma_init_hooks()` logs that RDMA transport is unavailable and aborts. This prevents silently accepting RDMA hook configuration in a build without RDMA support.
- `!SPDK_CONFIG_HAVE_EVP_MAC`: NVMe in-band authentication async, poll, and public qpair authenticate APIs return `-ENOTSUP`, with logging on entry points.

Role in the codebase:
- Keeps public/internal symbols available across reduced builds without forcing callers to scatter feature-conditionals.
- Makes unsupported features fail explicitly rather than linking to missing symbols.
- The RDMA hook stub is intentionally fatal, unlike CUSE/auth stubs, because installing RDMA hooks when RDMA is unavailable indicates an invalid build/runtime path.

Filesystem/storage relevance:
- Indirect storage infrastructure support. It controls feature availability for NVMe device presentation, RDMA transport hooks, and fabric authentication, all of which may affect how block devices are exposed to upper layers.
