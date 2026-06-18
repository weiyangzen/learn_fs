# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_srq.h

## Role

`hermon_srq.h` defines the Shared Receive Queue layer for the Hermon driver. It exposes the SRQ software handle layout, allocation/query/modify/post state carriers, SRQ constants, and the SRQ routines used by IBTF-facing CI code and internal queue management.

## Major Definitions

The file defines the default SRQ count shift, minimum SRQ size, maximum SGL count per SRQ WQE, and Hermon SRQ ownership/error states.

`hermon_sw_srq_s` is the core SRQ handle. It stores:
- Locking and state fields.
- SRQ number, protection domain, memory-region handle, user-mapping fields, UAR page, and devmap cookie.
- Real queue sizes, SRQC/WQ resources, callback argument, and reference count.
- Work-queue metadata, WQE buffer pointer, buffer size, WQE size shift, SGL count, and WQE counter.
- Doorbell record access handle, virtual/physical doorbell pointers, user map offset, zero-based descriptor offset, and queue allocation info.

The `_NOTE` annotations document read-only fields, lock-protected fields, and fields intentionally readable without holding `srq_lock`.

`hermon_srq_info_t` carries allocation inputs/outputs such as PD, IBT SRQ handle, requested and real sizes, result handle, and flags. `hermon_srq_options_t` exists for extended allocation options, currently queue-location selection.

## Interfaces

The exported routines allocate, free, modify, post receive WRs to, reference-count, and look up SRQs by SRQ number.

## Integration Notes

SRQs combine hardware context resources, WQE memory, memory registration, doorbell records, user mappings, and IBTF-visible handles. The file’s maximum SGL choice is a driver policy derived from firmware WQE-size limits.
