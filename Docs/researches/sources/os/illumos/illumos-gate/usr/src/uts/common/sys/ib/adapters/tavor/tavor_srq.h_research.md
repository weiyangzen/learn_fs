# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_srq.h

## Purpose

Defines Shared Receive Queue sizing, sync policy, SRQ state constants, the SRQ software handle, SRQ allocation options, and the Tavor SRQ public interface.

## Main Definitions

- Default SRQ count and size shifts for 128 MB and 256 MB profiles, minimum SRQ profile values, and minimum SRQ depth.
- `TAVOR_SRQ_MAX_SGL` caps SRQ SGLs at 15 due to documented firmware problems with larger SRQ WQEs.
- `TAVOR_SRQ_IS_SYNC_REQ()` mirrors QP sync policy for SRQ WQE memory based on config profile and queue placement.
- SRQC size constants and SRQ hardware/software ownership states.
- `struct tavor_sw_srq_s`: SRQ handle with lock, PD/MR handles, SRQ number, limit, sync flag, refcount, state, user mapping details, real sizes, context/handle resources, WQ buffer metadata, WRID lock/list, zero-based descriptor offset, and queue allocation info.
- Lock annotations distinguish read-only fields, data readable without lock, and `srq_lock`-protected mutable queue and size state.
- `tavor_srq_info_t`: allocation input/output bundle.
- `tavor_srq_options_t`: currently controls normal vs adapter DDR work queue allocation.
- Prototypes for SRQ allocate/free/modify/post, refcount inc/dec, and lookup by SRQ number.

## Integration Notes

SRQs are shared by QPs through `tavor_sw_qp_s::qp_srqhdl` and are posted through the work request path. The WRID and queue-lock types come from `tavor_wr.h`.

## Risks and Gotchas

- Firmware SGL limitations are encoded as a driver policy constant; increasing it can expose known hardware/firmware failure modes.
- SRQ WQE index/address macros live in `tavor_wr.h`, so SRQ buffer layout must remain compatible there.
- Refcounting is explicit because QPs can attach to a shared SRQ; free paths must coordinate with QP ownership.
