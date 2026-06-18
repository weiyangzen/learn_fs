# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/iser/iser_idm.h

## Purpose

Defines the iSER transport hooks visible to IDM, especially the target service creation routine and the copy-vs-registration threshold for small transfers.

## Main Definitions

- Includes IDM core and text interfaces.
- Documents that most transport functions are called through the IDM transport ops vector, while `iser_tgt_svc_create()` is also called from an async handler.
- `ISER_BCOPY_THRESHOLD` is `0x20000` bytes, selecting bcopy into pre-registered memory for transfers where memory registration would be too expensive.
- Declares `iser_tgt_svc_create(idm_svc_req_t *, struct idm_svc_s *)`.

## Integration Notes

This header is the IDM-facing glue point for iSER target service setup. It complements the broader service registration functions in `iser.h`.

## Risks and Gotchas

- The bcopy threshold is a performance policy: changing it shifts CPU cost vs RDMA registration overhead.
- `iser_tgt_svc_create()` may be invoked from more than one path, so implementation must handle async and ULP contexts safely.
