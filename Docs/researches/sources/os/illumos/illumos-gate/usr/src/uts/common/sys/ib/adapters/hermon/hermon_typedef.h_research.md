# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_typedef.h

## Role

`hermon_typedef.h` is the forward-declaration hub for the Hermon driver. It lets `hermon.h` include common opaque types before pulling in the rest of the driver headers.

## Major Definitions

The file declares aliases for the Hermon soft state, agent list, queue allocation info, resource pool and resource handles, WRID/work-queue support structures, ICM structures, DMA info, and many hardware mailbox/context structures.

Hardware typedefs cover firmware/query structures, port setup structures, MPT/CMPT/MTT/EQC/EQE/CQC/SRQC/UAR/CQE layouts, address paths, UD address vectors, QP contexts, multicast group entries, performance counters, and WQE segment layouts.

The file also defines the main software handle pointer typedefs:
- `hermon_mrhdl_t`, `hermon_mwhdl_t`, `hermon_pdhdl_t`
- `hermon_eqhdl_t`, `hermon_cqhdl_t`, `hermon_srqhdl_t`
- `hermon_fmrhdl_t`, `hermon_ahhdl_t`, `hermon_qphdl_t`
- `hermon_mcghdl_t`

## Interfaces

There are no function prototypes. The header only establishes names for structures defined elsewhere.

## Integration Notes

This file reduces include-order coupling across the Hermon driver. Many typedefs are opaque pointer handles used by IBTF-facing entry points, while hardware-layout typedefs make later headers readable without requiring full definitions up front.
