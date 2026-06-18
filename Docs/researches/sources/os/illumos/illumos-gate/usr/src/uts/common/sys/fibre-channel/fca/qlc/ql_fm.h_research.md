# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_fm.h

This header defines qlc-specific FMA ereport classes, fault IDs, report metadata, external DMA/access attributes, and FMA helper prototypes.

Key contents:
- QLogic device class string `QL_FM_DEVICE`.
- qlc-specific ereport class strings for DMA error, bad payload, command failure, chip hang, unknown errors, asynchronous mailbox request/response transfer errors, access-handle errors, and DMA-handle errors.
- Maximum ereport class length `QL_FM_MAX_CLASS`.
- `qlc_fm_ereport_t`, mapping fault ID, description, qlc eclass, generic eclass, and impact code.
- `qlc_fm_ereport_fid_t` enum for qlc fault IDs.
- External DDI access and DMA attribute declarations.
- FMA prototypes for access-handle checking, DMA-handle checking, DDI error callback, init/fini, impact reporting, service impact, and per-packet DMA-handle checking.

Dependencies:
- Uses `ql_adapter_state_t`, `ql_srb_t`, DDI FMA types, and DDI DMA/access types from including context.

Research notes:
- This is the qlc driver's FMA integration boundary.
- The ereport IDs align driver-detected hardware/DMA/command failures with illumos fault-management reporting.
