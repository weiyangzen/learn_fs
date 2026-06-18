# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_typedef.h

## Purpose

Provides forward typedefs for common Tavor driver structures and opaque handle aliases, allowing other Tavor headers to refer to shared objects before their full definitions are included.

## Main Definitions

- Forward typedefs for driver-global and resource infrastructure: `tavor_state_t`, agent lists, queue allocation info, resource pools, resources, WRID entries/lists, work queue headers, and work queue locks.
- Forward typedefs for hardware command/context/layout structures: HCR, query results, init/query HCA/IB structures, MPT/MTT, EQ/CQ/SRQ/UAR/CQE/QPC/MCG objects, address paths, UD address vectors, performance counters, and WQE segments.
- Opaque handle typedefs:
  - `tavor_mrhdl_t` and `tavor_mwhdl_t`
  - `tavor_pdhdl_t`
  - `tavor_eqhdl_t`
  - `tavor_cqhdl_t`
  - `tavor_srqhdl_t`
  - `tavor_ahhdl_t`
  - `tavor_qphdl_t`
  - `tavor_mcghdl_t`

## Integration Notes

The file is intended to be included early through `tavor.h`, before the rest of the Tavor driver headers. It prevents include cycles among hardware layout, resource, QP, CQ, MR, AH, MCG, and WR processing headers.

## Risks and Gotchas

- These are only forward declarations. Any file dereferencing the pointed-to handles must include the corresponding full-definition header.
- Opaque handle aliases all use pointer-to-struct forms; mixing handles is type-safe only to the extent the compiler sees distinct pointed-to struct tags.
