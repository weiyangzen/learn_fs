# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rsm/rsmapi_common.h

## Role

`rsmapi_common.h` defines common application-facing RSMAPI handle types, controller attributes, access-list entries, barrier wrapper, scatter-gather structures, and API flags.

## Types and Structures

It declares opaque local-memory and controller handles.

`rsmapi_controller_attr_t` reports direct/atomic access sizes, page size, export/import segment size limits, total import/export map limits, and segment counts.

`rsmapi_access_entry_t` maps a node ID to permissions.

`rsmapi_barrier_t` stores a segment pointer, generation number, and private data.

Scatter-gather I/O uses `rsm_iovec_t` entries, each identifying local memory by handle or virtual address plus local/remote offsets and transfer length. `rsm_scat_gath_t` wraps request/residual counts, flags, remote handle, and iovec pointer.

## Flags

I/O vector types are `RSM_HANDLE_TYPE` and `RSM_VA_TYPE`.

Export creation flags include rebind allowance and nonblocking segment creation. Scatter-gather flags include implicit signal post and no-accumulate signal post behavior.

## Research Notes

This header defines the user-visible shape of RSMAPI bulk-transfer and access-control operations. It must remain aligned with the kernel-agent equivalents in `rsm.h`.
