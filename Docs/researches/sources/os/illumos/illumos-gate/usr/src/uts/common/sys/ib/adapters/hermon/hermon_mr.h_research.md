# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_mr.h

## Purpose
Defines Hermon memory region/window support: MPT/MTT sizing defaults, deregistration levels, DMA bind descriptors, memory-region software handles, registration options, allocated-memory handle state, and MR/MW/FMR prototypes.

## Main Interfaces
- Defaults:
  - `HERMON_NUM_DMPT_SHIFT`
  - `HERMON_NUM_MTT_SHIFT`
  - `HERMON_MTT_SIZE_SHIFT`
  - `HERMON_MAX_MEM_MPT_SHIFT`
- Deregistration levels:
  - full deregistration
  - skip HW2SW MPT
  - skip HW2SW MPT and unbind
- `HERMON_MR_REUSE_DMAHDL()` determines when an existing DMA handle may be reused during reregistration.
- `hermon_sw_refcnt_t`: MTT sharing reference counter with helper macros.
- `hermon_bind_info_t`: DMA bind inputs and outputs for vaddr, buf, user buffer, LKey, flags, bypass mode, cookie count, and DMA-handle ownership.
- `struct hermon_sw_mr_s`: software MR/MW handle with lock, MPT/MTT/refcount resources, PD, bind info, access flags, keys, page sizing, MPT type, FMR/user-memory metadata, and unpin callback.
- `hermon_mr_options_t`: optional bind DMA handle, bind type, and virtual-address override policy.
- `struct ibc_mem_alloc_s`: DMA/access handles for CI memory allocation entry points.
- Prototypes cover DMA MR registration, normal/buffer/shared/reregister paths, MTT bind/unbind, deregister/query/sync, MW alloc/free, key calculation, FMR allocation/deallocation/registration, LKey allocation, and FCoIB FEXCH MPT init/fini.

## Dependencies And Relationships
Used by QP/CQ/EQ/SRQ queue memory registration, user memory pinning, FMR, FCoIB, and TPT command posting. Hardware MPT/MTT formats are in `hermon_hw.h`; command submission is declared in `hermon_cmd.h`.

## Research Notes
The header separates dMPT/cMPT ownership policy through `hermon_mpt_rsrc_type_t` and `HERMON_NO_MPT_OWNERSHIP`/`HERMON_PASS_MPT_OWNERSHIP`, reflecting Hermon’s mixed use of hardware-owned and driver-tracked MPT-like contexts.
