# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rsm/rsm_common.h

## Role

`rsm_common.h` defines common RSM/RSMAPI/RSMPI versioning, error codes, segment/service ID ranges, permission bits, direct-access sizes, core handle types, and barrier representation.

## Error and ID Spaces

`RSM_VERSION` is 5. Return codes cover API misuse, bad handles, publication/mapping state errors, permissions, barriers, resource exhaustion, unreachable nodes, connection aborts, timeouts, and bad configuration. RSMPI-specific errors start at 101 and include driver/controller registration, memory binding, handler, queue, and communication failures.

Segment/service ID ranges partition driver-private, cluster transport, library, DLPI, HPC, OPS, and user application spaces.

## Types

The header defines:
- `rsm_addr_t`, `rsm_node_id_t`, `rsm_memseg_id_t`, `rsm_permission_t`.
- import/export segment handle opaque pointer types.
- permissions `RSM_PERM_NONE`, `RSM_PERM_READ`, `RSM_PERM_WRITE`, `RSM_PERM_RDWR`.
- direct-access size enum values for 8/16/32/64-bit access.
- barrier types and barrier mode.

`rsm_barrier_t` is four `rsm_barrier_component_t` unions, each capable of holding integer, byte, char, or pointer representations.

## Research Notes

This is the foundational stable RSM type/error header. Numeric error values and ID ranges are central ABI contracts for both user and provider sides.
