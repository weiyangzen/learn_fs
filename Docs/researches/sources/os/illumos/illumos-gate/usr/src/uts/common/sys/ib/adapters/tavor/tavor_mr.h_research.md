# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_mr.h

## Role

`tavor_mr.h` defines Tavor memory-region and memory-window support. It provides MPT/MTT sizing constants, deregistration policy flags, DMA binding metadata, software MR handle state, registration options, and IBTF-facing MR/MW routines.

## Major Definitions

The file defines default and minimal MPT counts, MPT entry size, MTT entry size, MTT segment size, default/minimal MTT segment counts, and `TAVOR_NUMMTT_TO_MTTSEG()` for rounding MTT entries to segments. It also defines the MTT page-walk version and maximum memory-region/window size shifts for supported DDR profiles.

Deregistration levels specify whether to free all resources, skip HW2SW_MPT, or skip both HW2SW_MPT and unbind. `TAVOR_MR_REUSE_DMAHDL()` determines whether an existing DMA handle can be reused when bypass/noncoherent mapping constraints allow.

`tavor_sw_refcnt_t` tracks shared MTT reference counts for shared memory regions, with helpers to initialize and test sharing.

`tavor_bind_info_t` records the data needed for DMA binding: address, length, address space, buf pointer, DMA handle, current DMA cookie, cookie count, bind type, flags, bypass mode, and whether to free the DMA handle. Bind types cover none, virtual address, buf, and user buf.

`tavor_sw_mr_s` stores MR lock, MPT/MTT/refcount resources, PD handle, bind info, access flags, LKey/RKey, MTT page size, software resource, user-memory flag/cookie, and unpin callback data. `tavor_mr_options_t` provides optional DMA handle, bind type, and zero-based/override address behavior.

## Interfaces

The header declares DMA MR registration, virtual-address and buf registration, MTT bind/unbind, shared registration, deregistration, query, reregister variants, sync, memory-window allocate/free, and key calculation.

## Integration Notes

This header ties IBTF memory verbs to illumos DDI DMA binding and Tavor MPT/MTT firmware ownership. Reference counting is essential because shared MRs have distinct MPTs but may share MTT resources.
