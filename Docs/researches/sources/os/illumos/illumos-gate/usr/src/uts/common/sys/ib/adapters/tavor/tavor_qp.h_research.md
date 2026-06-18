# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_qp.h

## Purpose

Defines the Tavor InfiniBand adapter driver's Queue Pair resource constants, QP software handle layout, QPN tracking entries, allocation options, and cross-file QP management prototypes.

## Main Definitions

- QP sizing/configuration defaults for 128 MB and 256 MB adapter DDR profiles, minimum profile values, and minimum QP depth.
- `TAVOR_QP_IS_SYNC_REQ()` decides whether work queue memory needs `ddi_dma_sync()` based on config profile and queue location.
- QPC, extended QPC, RDB sizing, RDMA read/atomic limits, maximum WQE SGL count, QP number mask, schedule queue mapping, AckReq frequency, and max message size constants.
- `TAVOR_QP_WQ_ALIGN()` computes combined work-queue alignment to avoid hardware 32-bit boundary restrictions.
- `TAVOR_QP_TYPE_VALID()` maps IBTF transport service types to Tavor QP service types.
- `tavor_qp_wq_type_t` and WQE header overhead constants used to calculate WQE sizes and SGL capacity.
- `tavor_qp_info_t`: internal input/output bundle for normal and special QP allocation.
- `tavor_qpn_entry_t`: AVL-tracked QPN allocation/refcount entry, with release/free flags.
- `struct tavor_sw_qp_s`: the main QP handle, containing lock-protected state, PD/MR/CQ handles, SQ/RQ buffers and WRID headers, QPC/RDB resources, SRQ association, multicast refcount, saved MTU/static rate, user mapping details, and embedded hardware QPC shadow.
- `tavor_qp_options_t`: currently controls work queue memory placement.
- Prototypes for QP alloc/free/query, special QP allocation, QPN AVL management, QP lookup by number, QP modify, and reset transition.

## Integration Notes

This header is consumed by the Tavor CI/IBTF implementation and by lower-level work request and completion paths. It depends on common Tavor typedefs, IBTF allocation/query/modify types, `tavor_qalloc_info_s`, `tavor_hw_qpc_s`, and related resource handles.

`struct tavor_sw_qp_s` is the central software object tying together hardware context, queue memory, protection domain, CQs, optional SRQ, and completion WRID tracking.

## Risks and Gotchas

- QP memory alignment and sync behavior are hardware-sensitive; changing sizing or queue-location logic can break DMA correctness.
- The SQ/RQ fields have explicit lock annotations; posting, completion, reset, and free paths must preserve those lock boundaries.
- QPNs are 24-bit and additionally tracked in an AVL tree with refcounts; release semantics differ for normal release vs free-only paths.
- Special QPs carry port and P_Key state in the same handle structure as ordinary QPs.
