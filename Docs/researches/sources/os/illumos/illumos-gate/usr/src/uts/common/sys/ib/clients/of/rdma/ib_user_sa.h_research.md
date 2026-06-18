# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/rdma/ib_user_sa.h

## Purpose

Defines the OFED-compatible user SA path record structure.

## Main Definitions

- Imported-license comment for OFED `ib_user_sa.h`.
- `struct ib_user_path_rec` containing:
  - DGID and SGID byte arrays.
  - Destination/source LIDs.
  - Raw traffic, flow label, reversibility, MTU, P_Key.
  - Hop limit, traffic class, number of paths, service level.
  - MTU/rate/packet lifetime selectors and values.
  - Preference.

## Integration Notes

This is a compact user ABI counterpart to the kernel `ib_sa_path_rec` in `ofed_kernel.h`.

## Risks and Gotchas

- Uses fixed byte arrays for GIDs rather than `union ib_gid`, preserving user ABI layout.
- Field sizes/order must remain compatible with OFED userland.
